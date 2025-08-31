Degradation System
==================

The SegnoMMS degradation system provides graceful handling of unsupported features and configurations through automatic fallbacks while maintaining QR code scanability and visual quality.

Overview
--------

The degradation system:

* **Detects Unsupported Features**: Automatically identifies features not available in the current configuration
* **Applies Smart Fallbacks**: Uses intelligent alternatives that maintain visual similarity and functionality
* **Maintains Scanability**: Ensures QR codes remain scannable after degradation
* **Provides Transparency**: Reports all degradations with detailed reasoning
* **Integrates Seamlessly**: Works automatically with both direct and intent-based APIs

Architecture
------------

.. autoclass:: segnomms.degradation.manager.DegradationManager
   :members:
   :undoc-members:
   :show-inheritance:

The degradation system consists of:

1. **DegradationManager**: Central orchestrator that applies degradation rules
2. **DegradationRule**: Individual rules that check for and handle specific issues
3. **DegradationResult**: Comprehensive result containing warnings and modifications
4. **Warning System**: Structured warnings with actionable suggestions

Core Components
---------------

DegradationResult
~~~~~~~~~~~~~~~~~

.. autoclass:: segnomms.degradation.models.DegradationResult
   :members:
   :undoc-members:
   :show-inheritance:

Contains comprehensive information about what was degraded and why.

DegradationWarning
~~~~~~~~~~~~~~~~~~

.. autoclass:: segnomms.degradation.models.DegradationWarning
   :members:
   :undoc-members:
   :show-inheritance:

Structured warning information with context and suggestions.

WarningLevel
~~~~~~~~~~~~

.. autoclass:: segnomms.degradation.models.WarningLevel
   :members:
   :undoc-members:
   :show-inheritance:

Severity levels for degradation warnings.

Built-in Degradation Rules
---------------------------

SegnoMMS includes comprehensive degradation rules that handle common compatibility issues:

Shape Degradation
~~~~~~~~~~~~~~~~~

Handles unsupported module shapes:

* **pyramid** → **squircle**: Maintains rounded aesthetic
* **hexagon** → **circle**: Preserves geometric simplicity
* **star** → **diamond**: Similar angular appearance
* **complex-shape** → **square**: Safe fallback for compatibility

.. code-block:: python

   from segnomms.config import RenderingConfig
   from segnomms.degradation.manager import DegradationManager

   # Request unsupported shape
   config = RenderingConfig.from_kwargs(shape="pyramid")

   manager = DegradationManager()
   degraded_config, result = manager.apply_degradation(config)

   # Check what happened
   for warning in result.warnings:
       print(f"Degraded: {warning.feature}")
       print(f"From: {warning.original_value}")
       print(f"To: {warning.fallback_value}")
       print(f"Reason: {warning.reason}")

Frame Degradation
~~~~~~~~~~~~~~~~~

Handles complex frame configurations:

.. code-block:: python

   # Unsupported frame configuration
   config = RenderingConfig.from_kwargs(
       frame_shape="star",
       frame_clip_mode="gradient"
   )

   degraded_config, result = manager.apply_degradation(config)

   # Automatic fallbacks applied
   assert degraded_config.frame.shape == "circle"  # Rounded fallback
   assert degraded_config.frame.clip_mode == "fade"  # Supported mode

Color and Accessibility Degradation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensures accessibility standards are maintained:

.. code-block:: python

   # Poor contrast configuration
   config = RenderingConfig.from_kwargs(
       dark="#888888",
       light="#999999"  # Very low contrast
   )

   degraded_config, result = manager.apply_degradation(config)

   # Colors adjusted for accessibility
   contrast_warning = next(w for w in result.warnings if "contrast" in w.feature)
   print(f"Improved contrast: {contrast_warning.fallback_value}")

Advanced Features Degradation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handles advanced QR features not supported in all contexts:

.. code-block:: python

   # Complex advanced configuration
   config = RenderingConfig(
       advanced_qr=AdvancedQRConfig(
           structured_append=True,
           symbol_count=5,  # Too many symbols
           mask_pattern=8   # Invalid pattern
       )
   )

   degraded_config, result = manager.apply_degradation(config)

   # Advanced features adjusted
   assert degraded_config.advanced_qr.symbol_count <= 4
   assert 0 <= degraded_config.advanced_qr.mask_pattern <= 7

Custom Degradation Rules
------------------------

Create custom rules for specific use cases:

.. code-block:: python

   from segnomms.degradation.rules import DegradationRule
   from segnomms.degradation.models import DegradationWarning, WarningLevel
   from segnomms.config import RenderingConfig
   from typing import Optional

   class CustomShapeDegradationRule(DegradationRule):
       """Custom rule for organization-specific shape restrictions."""

       def __init__(self):
           self.allowed_shapes = {"square", "circle", "rounded"}
           self.fallback_shape = "square"

       def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
           """Check if shape is allowed in organization policy."""
           current_shape = str(config.geometry.shape)

           if current_shape not in self.allowed_shapes:
               # Apply degradation
               config.geometry.shape = self.fallback_shape

               return DegradationWarning(
                   feature="geometry.shape",
                   level=WarningLevel.WARNING,
                   reason=f"Shape '{current_shape}' not allowed by organization policy",
                   original_value=current_shape,
                   fallback_value=self.fallback_shape,
                   suggestion=f"Use one of: {', '.join(self.allowed_shapes)}",
                   context={
                       "policy": "organization_shapes",
                       "allowed_shapes": list(self.allowed_shapes)
                   }
               )

           return None

   # Use custom rule
   custom_manager = DegradationManager(rules=[CustomShapeDegradationRule()])
   config = RenderingConfig.from_kwargs(shape="pyramid")

   degraded_config, result = custom_manager.apply_degradation(config)
   assert degraded_config.geometry.shape == "square"

Integration with Intent System
------------------------------

The degradation system integrates seamlessly with the intent-based API:

.. code-block:: python

   from segnomms import SegnoMMS
   from segnomms.intents.models import IntentsConfig, StyleIntents, FrameIntents

   renderer = SegnoMMS()

   # Request features that will require degradation
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="pyramid",  # Will be degraded
           patterns={"finder": "hexagon"}  # Will be degraded
       ),
       frame=FrameIntents(
           shape="star",  # Will be degraded
           clip_mode="gradient"  # Will be degraded
       )
   )

   result = renderer.render_with_intents("Hello World", intents)

   # Analyze degradation results
   print(f"Generated QR with {len(result.warnings)} degradations:")

   for warning in result.warnings:
       if warning.code == "FEATURE_DEGRADED":
           print(f"  {warning.detail}")
           print(f"    Original: {warning.context.get('original_value')}")
           print(f"    Applied: {warning.context.get('fallback_value')}")
           print(f"    Reason: {warning.context.get('reason')}")

   # QR code still fully functional despite degradations
   assert result.scanability_prediction >= 0.9

Production Monitoring
---------------------

Monitor degradation patterns in production:

.. code-block:: python

   from collections import defaultdict
   from typing import Dict, List
   import json

   class DegradationMonitor:
       """Monitor degradation patterns for system analysis."""

       def __init__(self):
           self.feature_degradations = defaultdict(int)
           self.fallback_usage = defaultdict(int)
           self.user_patterns = defaultdict(list)

       def record_degradation(self, result: RenderingResult, user_id: str = None):
           """Record degradation event for analysis."""
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   feature = warning.context.get('original_feature', 'unknown')
                   fallback = warning.context.get('fallback_feature', 'unknown')

                   self.feature_degradations[feature] += 1
                   self.fallback_usage[f"{feature}->{fallback}"] += 1

                   if user_id:
                       self.user_patterns[user_id].append({
                           "feature": feature,
                           "fallback": fallback,
                           "timestamp": warning.context.get('timestamp'),
                           "reason": warning.context.get('reason')
                       })

       def generate_report(self) -> Dict:
           """Generate degradation analytics report."""
           total_degradations = sum(self.feature_degradations.values())

           return {
               "summary": {
                   "total_degradations": total_degradations,
                   "unique_features": len(self.feature_degradations),
                   "most_degraded_feature": max(
                       self.feature_degradations.items(),
                       key=lambda x: x[1]
                   ) if total_degradations > 0 else None
               },
               "feature_breakdown": dict(self.feature_degradations),
               "fallback_patterns": dict(self.fallback_usage),
               "recommendations": self._generate_recommendations()
           }

       def _generate_recommendations(self) -> List[str]:
           """Generate recommendations based on degradation patterns."""
           recommendations = []

           # High degradation features
           for feature, count in self.feature_degradations.items():
               if count > 100:  # Threshold for "frequent"
                   recommendations.append(
                       f"Consider implementing native support for '{feature}' "
                       f"(degraded {count} times)"
                   )

           # Common fallback patterns
           common_fallbacks = {
               k: v for k, v in self.fallback_usage.items() if v > 50
           }

           if common_fallbacks:
               recommendations.append(
                   "Consider promoting these fallback patterns to first-class features: "
                   f"{list(common_fallbacks.keys())}"
               )

           return recommendations

   # Usage in production
   monitor = DegradationMonitor()

   # Record degradations
   result = renderer.render_with_intents(payload, intents)
   monitor.record_degradation(result, user_id="user123")

   # Generate periodic reports
   report = monitor.generate_report()
   print(json.dumps(report, indent=2))

Performance Considerations
---------------------------

The degradation system is designed for minimal performance impact:

* **Rule Evaluation**: O(1) for most common rules
* **Memory Usage**: Minimal overhead, only stores warnings
* **Caching**: Rule results can be cached for repeated configurations
* **Lazy Evaluation**: Only evaluates rules when needed

.. code-block:: python

   # Disable degradation for performance-critical paths
   manager = DegradationManager()
   manager.enabled = False  # Skip all degradation processing

   # Or use selective rule application
   critical_rules = [ShapeCompatibilityRule(), ColorContrastRule()]
   fast_manager = DegradationManager(rules=critical_rules)

Best Practices
--------------

1. **Monitor Degradation Patterns**: Track which features are frequently degraded
2. **Test Edge Cases**: Verify degradation behavior with extreme configurations
3. **Customize Rules**: Create organization-specific degradation policies
4. **Handle Warnings**: Always check and respond to degradation warnings
5. **Performance Monitoring**: Monitor degradation impact on processing time
6. **User Education**: Inform users about why features were degraded
7. **Graceful Failure**: Ensure degraded configurations still produce usable QR codes

Future Enhancements
-------------------

Planned improvements to the degradation system:

* **Machine Learning**: AI-powered degradation decisions based on usage patterns
* **A/B Testing**: Automatic testing of different degradation strategies
* **Predictive Degradation**: Pre-validate configurations before processing
* **Custom Policies**: GUI for creating organization-specific degradation rules
* **Real-time Analytics**: Live monitoring of degradation patterns and impact
