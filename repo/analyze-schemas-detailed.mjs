#!/usr/bin/env node
/**
 * Get detailed property lists for webhook schemas
 */

import WEBHOOK_SCHEMA from "@octokit/webhooks-schemas" with { type: "json" };

// Check all pull_request schemas for "opened"
const openedSchemas = Object.keys(WEBHOOK_SCHEMA.definitions || {})
  .filter(key => key.includes('opened'));

console.log("Schemas with 'opened':", openedSchemas);

// Look specifically for pull_request opened
if (WEBHOOK_SCHEMA.definitions['pull_request$opened']) {
  const schema = WEBHOOK_SCHEMA.definitions['pull_request$opened'];
  console.log("\n=== Complete pull_request$opened Schema Properties ===");
  console.log("Required:", schema.required);
  console.log("Additional properties:", schema.additionalProperties);
  console.log("All properties:");
  Object.keys(schema.properties || {}).forEach(prop => {
    const propDef = schema.properties[prop];
    console.log(`  ${prop}: ${JSON.stringify(propDef).substring(0, 100)}...`);
  });
}

// Search for push in the oneOf array more thoroughly
console.log("\n=== Searching for Push Schema ===");
WEBHOOK_SCHEMA.oneOf.forEach((schema, index) => {
  if (schema.properties) {
    const props = Object.keys(schema.properties);
    if (props.includes('ref') && props.includes('commits') && props.includes('head_commit')) {
      console.log(`Found potential push schema at index ${index}`);
      console.log("Properties:", props);
      console.log("Required:", schema.required || []);
      console.log("Additional properties:", schema.additionalProperties);
    }
  }
});
