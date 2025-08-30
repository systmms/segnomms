#!/usr/bin/env node
/**
 * Validate GitHub Actions event payload fixtures.
 *
 * Usage (Lefthook will pass files): node repo/gha/scripts/validate-event-payloads.mjs --format {staged_files}
 * Manual: node repo/gha/scripts/validate-event-payloads.mjs repo/gha/events/*.json repo/gha/tests/**\/*.json
 *
 * Flags:
 *   --format       Pretty-print JSON (stable key order) if changes are detected.
 *   --git-add      Re-stage changed files (useful if not using lefthook `stage_fixed: true`).
 *
 * The script always provides verbose error messages and fix suggestions by default.
 */

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import WEBHOOK_SCHEMA from "@octokit/webhooks-schemas" with { type: "json" }; // combined JSON Schema

// ---------- CLI args ----------
const args = process.argv.slice(2);
const shouldFormat = args.includes("--format");
const shouldGitAdd = args.includes("--git-add");
const isVerbose = true; // Always verbose for better error messages
const shouldSuggestFix = true; // Always provide suggestions
const files = args.filter((a) => !a.startsWith("--"));

if (files.length === 0) {
  console.error(
    "[validate-event-payloads] No files passed. Pass files explicitly or via Lefthook `{staged_files}`."
  );
  process.exit(0);
}

// ---------- Ajv setup ----------
const ajv = new Ajv({ strict: true, allErrors: true });
addFormats(ajv);
// Octokit schemas use a custom keyword; declare it so Ajv doesn't error in strict mode.
ajv.addKeyword("tsAdditionalProperties"); // @octokit/webhooks-schemas guidance

const validateWebhook = ajv.compile(WEBHOOK_SCHEMA);

// Minimal schemas for non-webhook events that `act` supports (no official webhook schema exists)
const FALLBACK_SCHEMAS = {
  workflow_dispatch: {
    $id: "workflow_dispatch",
    type: "object",
    properties: {
      inputs: { type: "object", additionalProperties: true },
    },
    additionalProperties: true,
  },
  schedule: {
    $id: "schedule",
    type: "object",
    additionalProperties: true, // usually unused; `act schedule` works without a payload file
  },
};

// ---------- helpers ----------
function sortKeysDeep(value) {
  if (Array.isArray(value)) return value.map(sortKeysDeep);
  if (value && typeof value === "object") {
    return Object.keys(value)
      .sort()
      .reduce((acc, k) => {
        acc[k] = sortKeysDeep(value[k]);
        return acc;
      }, {});
  }
  return value;
}

function prettyWriteIfChanged(file, obj) {
  const formatted = JSON.stringify(sortKeysDeep(obj), null, 2) + "\n";
  const existing = fs.readFileSync(file, "utf8");
  if (existing !== formatted) {
    fs.writeFileSync(file, formatted, "utf8");
    return true;
  }
  return false;
}

function guessEventName(filePath, json) {
  // For GitHub Actions testing, normalize pull_request event names
  const base = path.basename(filePath, ".json");

  // All pull_request variants should be treated as "pull_request" for act testing
  if (base && base.startsWith("pull_request")) return "pull_request";

  // Other specific events
  if (base === "workflow_dispatch" || base === "push" || base === "schedule") return base;

  // Heuristics from payload keys (best-effort)
  if (json && typeof json === "object") {
    if (json.inputs) return "workflow_dispatch";
    if (json.pull_request) return "pull_request";
    if (json.issue) return "issues";
    if (json.ref || json.head_commit) return "push";
  }
  return "unknown";
}

function resolveSchemaRef(refPath, schema = WEBHOOK_SCHEMA) {
  if (!refPath.startsWith("#/")) return null;
  const path = refPath.substring(2).split("/");
  let current = schema;
  for (const segment of path) {
    current = current[segment];
    if (!current) return null;
  }
  return current;
}

function extractRequiredProperties(schemaObj) {
  const required = new Set(schemaObj.required || []);
  const properties = schemaObj.properties || {};

  // Handle allOf schemas (common in webhook schemas)
  if (schemaObj.allOf) {
    for (const subSchema of schemaObj.allOf) {
      if (subSchema.$ref) {
        const resolved = resolveSchemaRef(subSchema.$ref);
        if (resolved) {
          (resolved.required || []).forEach(prop => required.add(prop));
        }
      } else {
        (subSchema.required || []).forEach(prop => required.add(prop));
      }
    }
  }

  return { required: Array.from(required), properties };
}

function findMatchingWebhookSchema(json, errors) {
  if (!json || typeof json !== "object") return null;

  // For pull_request events, match the specific action-based schema
  if (json.pull_request && json.action) {
    const eventName = `pull_request$${json.action}`;
    if (WEBHOOK_SCHEMA.definitions[eventName]) {
      return { name: eventName, schema: WEBHOOK_SCHEMA.definitions[eventName] };
    }
  }

  // For push events, use the push$event definition
  if (json.ref && json.commits && !json.action) {
    if (WEBHOOK_SCHEMA.definitions["push$event"]) {
      return { name: "push", schema: WEBHOOK_SCHEMA.definitions["push$event"] };
    }
  }

  // For issues events
  if (json.issue) {
    const action = json.action || "opened";
    const eventName = `issues$${action}`;
    if (WEBHOOK_SCHEMA.definitions[eventName]) {
      return { name: eventName, schema: WEBHOOK_SCHEMA.definitions[eventName] };
    }
  }

  return null;
}

function categorizeErrors(errors, json, matchingSchema) {
  const categorized = {
    missing: [],
    extra: [],
    typeErrors: [],
    other: []
  };

  // Use Sets to avoid duplicates
  const seenMissing = new Set();
  const seenExtra = new Set();
  const seenTypeErrors = new Set();

  for (const error of errors) {
    const path = error.instancePath || "/";

    if (error.keyword === "required") {
      const field = error.params?.missingProperty || "unknown";
      const key = `${path}:${field}`;
      if (!seenMissing.has(key)) {
        seenMissing.add(key);
        categorized.missing.push({
          field: field,
          path: path,
          message: error.message
        });
      }
    } else if (error.keyword === "additionalProperties") {
      const field = error.params?.additionalProperty || "unknown";
      const key = `${path}:${field}`;
      if (!seenExtra.has(key)) {
        seenExtra.add(key);
        categorized.extra.push({
          field: field,
          path: path,
          message: error.message
        });
      }
    } else if (error.keyword === "type" || error.keyword === "enum") {
      const field = path.split("/").pop() || "root";
      const key = `${path}:${field}`;
      if (!seenTypeErrors.has(key)) {
        seenTypeErrors.add(key);
        categorized.typeErrors.push({
          field: field,
          path: path,
          expected: error.params?.allowedValues || error.params?.type,
          actual: typeof (path === "/" ? json : json[field]),
          message: error.message
        });
      }
    } else {
      categorized.other.push({
        field: path.split("/").pop() || "root",
        path: path,
        message: error.message,
        keyword: error.keyword
      });
    }
  }

  return categorized;
}

function generateActionableErrorMessage(file, errors, json, eventName) {
  const matchingSchema = findMatchingWebhookSchema(json, errors);
  const categorized = categorizeErrors(errors, json, matchingSchema);

  let message = `❌ ${file}: ${eventName} event validation failed\n`;

  if (matchingSchema) {
    const { required, properties } = extractRequiredProperties(matchingSchema.schema);
    message += `\n   Expected schema: ${matchingSchema.name}\n`;

    if (categorized.missing.length > 0) {
      message += `\n   Missing required fields:\n`;
      for (const missing of categorized.missing.slice(0, 5)) {
        const propInfo = properties[missing.field];
        const typeInfo = propInfo?.type ? ` (${propInfo.type})` : "";
        const enumInfo = propInfo?.enum ? ` - Must be one of: ${propInfo.enum.join(", ")}` : "";
        message += `   • ${missing.field}${typeInfo}${enumInfo}\n`;
      }
    }

    if (categorized.extra.length > 0) {
      message += `\n   Unexpected fields (should be removed):\n`;
      for (const extra of categorized.extra.slice(0, 5)) {
        message += `   • ${extra.field}\n`;
      }
    }

    if (categorized.typeErrors.length > 0) {
      message += `\n   Type mismatches:\n`;
      for (const typeError of categorized.typeErrors.slice(0, 3)) {
        message += `   • ${typeError.field}: expected ${typeError.expected}, got ${typeError.actual}\n`;
      }
    }

    if (isVerbose && required.length > 0) {
      message += `\n   All required fields: ${required.join(", ")}\n`;
    }

    if (shouldSuggestFix) {
      message += `\n   💡 Consider using a working example from gha/tests/ as a template\n`;
    }
  } else {
    // Fallback to basic error reporting when we can't identify the schema
    message += `\n   Schema detection failed. Raw validation errors:\n`;
    for (const error of errors.slice(0, 5)) {
      message += `   • ${error.instancePath || "/"} ${error.message}\n`;
    }
  }

  return message;
}

// ---------- main ----------
let hadError = false;
let changedFiles = [];

for (const file of files) {
  if (!file.endsWith(".json")) continue;
  if (!fs.existsSync(file)) continue;

  let data;
  try {
    const raw = fs.readFileSync(file, "utf8");
    data = JSON.parse(raw);
  } catch (e) {
    console.error(`❌ ${file}: invalid JSON (${e.message})`);
    hadError = true;
    continue;
  }

  const eventName = guessEventName(file, data);

  // 1) Try validating as a webhook payload (covers push, pull_request, issues, etc.)
  let valid = validateWebhook(data);

  // 2) If that fails AND we recognize a non-webhook event, validate with fallback
  if (!valid && (eventName === "workflow_dispatch" || eventName === "schedule")) {
    const v = ajv.compile(FALLBACK_SCHEMAS[eventName]);
    valid = v(data);
    if (!valid) {
      // Use basic error reporting for non-webhook events since schema is simpler
      console.error(`❌ ${file}: invalid ${eventName} payload`);
      (v.errors || []).slice(0, 5).forEach((err) =>
        console.error(`   • ${err.instancePath || "/"} ${err.message}`)
      );
      hadError = true;
      continue;
    }
  }

  if (!valid) {
    const errorMessage = generateActionableErrorMessage(
      file,
      validateWebhook.errors || [],
      data,
      eventName
    );
    console.error(errorMessage);
    hadError = true;
    continue;
  }

  // Optional: canonicalize JSON to reduce diff churn
  if (shouldFormat) {
    const changed = prettyWriteIfChanged(file, data);
    if (changed) changedFiles.push(file);
  }

  console.log(`✅ ${file} (${eventName})`);
}

// Optionally re-stage formatted files (when not using lefthook's stage_fixed)
if (changedFiles.length && shouldGitAdd) {
  spawnSync("git", ["add", ...changedFiles], { stdio: "inherit" });
}

process.exit(hadError ? 1 : 0);
