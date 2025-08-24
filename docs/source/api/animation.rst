Animation and Effects
=====================

The Segno Interactive SVG Plugin provides comprehensive CSS-based animation capabilities for QR codes, 
focusing on performance, accessibility, and visual appeal.

Overview
--------

All animations are implemented using CSS keyframes and transitions, ensuring:

* Broad browser compatibility
* Hardware-accelerated performance  
* Automatic accessibility support
* Zero JavaScript dependencies

Animation Parameters
--------------------

The following animation parameters can be passed to the :func:`~segnomms.write` function or used 
with the intent-based API:

Fade-In Animation
~~~~~~~~~~~~~~~~~

.. py:data:: animation_fade_in
   :type: bool
   :value: False

   Enable fade-in animation for QR code modules. Modules fade from 80% scale and 0% opacity 
   to full size and opacity.

.. py:data:: animation_fade_duration  
   :type: float
   :value: 0.5

   Duration of fade-in animation in seconds. Valid range: 0.1 to 5.0.

.. py:data:: animation_timing
   :type: str
   :value: "ease"

   CSS timing function for animations. Options include:
   
   * ``"ease"`` - Slow start and end (default)
   * ``"ease-in"`` - Slow start
   * ``"ease-out"`` - Slow end
   * ``"ease-in-out"`` - Slow start and end
   * ``"linear"`` - Constant speed

Staggered Animation
~~~~~~~~~~~~~~~~~~~

.. py:data:: animation_stagger
   :type: bool
   :value: False

   Enable staggered animation where modules animate with progressive delays, creating a 
   wave-like reveal effect.

.. py:data:: animation_stagger_delay
   :type: float
   :value: 0.02

   Delay between module animations in seconds. Valid range: 0.01 to 0.5.
   
   .. note::
      Total reveal time is automatically capped at 800ms to maintain scanability.

Pulse Effect
~~~~~~~~~~~~

.. py:data:: animation_pulse
   :type: bool
   :value: False

   Enable pulse effect on finder patterns. Creates decorative halos that pulse behind 
   the finder patterns while keeping the actual patterns static for scanability.

Usage Examples
--------------

Basic Fade-In
~~~~~~~~~~~~~

.. code-block:: python

   import segno
   from segnomms import write
   
   qr = segno.make("Hello World")
   
   # Simple fade-in animation
   with open('fade.svg', 'w') as f:
       write(qr, f,
             animation_fade_in=True,
             animation_fade_duration=0.6,
             scale=10)

Staggered Wave Effect
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Wave-like reveal effect
   with open('wave.svg', 'w') as f:
       write(qr, f,
             animation_fade_in=True,
             animation_stagger=True,
             animation_stagger_delay=0.015,
             animation_timing="ease-out",
             scale=10)

Full Animation Suite
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # All animations combined
   with open('animated.svg', 'w') as f:
       write(qr, f,
             animation_fade_in=True,
             animation_fade_duration=0.5,
             animation_stagger=True,
             animation_stagger_delay=0.02,
             animation_pulse=True,
             animation_timing="ease-in-out",
             scale=10)

Intent-Based API
~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms import SegnoMMS
   from segnomms.intents.models import IntentsConfig, AnimationIntents
   
   renderer = SegnoMMS()
   
   intents = IntentsConfig(
       animation=AnimationIntents(
           fade_in=True,
           fade_duration=0.8,
           stagger_animation=True,
           stagger_delay=0.025,
           pulse_effect=True,
           transition_timing="ease-out"
       )
   )
   
   result = renderer.render_with_intents("Hello World", intents)

Technical Details
-----------------

CSS Variable Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The stagger animation uses CSS variables for efficient scaling:

.. code-block:: css

   .qr-module {
       animation-delay: calc(var(--i, 0) * var(--stagger-step));
   }

Each module receives a ``--i`` CSS variable with its index, eliminating the need for 
thousands of nth-child selectors.

Transform Geometry
~~~~~~~~~~~~~~~~~~

All animated elements are configured with proper transform geometry:

.. code-block:: css

   .qr-module {
       transform-box: fill-box;
       transform-origin: center;
       animation-fill-mode: both;
   }

This prevents animation wiggle and ensures smooth, centered transforms.

Accessibility
-------------

Reduced Motion Support
~~~~~~~~~~~~~~~~~~~~~~

All animations automatically respect the ``prefers-reduced-motion`` media query:

.. code-block:: css

   @media (prefers-reduced-motion: reduce) {
       .qr-root * {
           animation: none !important;
           transition: none !important;
       }
   }

Print Optimization
~~~~~~~~~~~~~~~~~~

Animations are disabled in print stylesheets for clean output:

.. code-block:: css

   @media print {
       .qr-root * {
           animation: none !important;
       }
   }

Performance Considerations
--------------------------

* **Maximum modules**: ~2,500 for smooth animation
* **Recommended stagger delay**: 0.01-0.03 seconds
* **Total reveal time**: Capped at 800ms
* **CSS size overhead**: ~2KB per animated QR code
* **Browser support**: All modern browsers with graceful degradation

Best Practices
--------------

1. **Scanability First**: Keep animations subtle and quick
2. **Context Appropriate**: Consider whether animation adds value
3. **Test Accessibility**: Always verify with reduced motion enabled
4. **Performance Testing**: Test on lower-end devices
5. **Fallback Ready**: Ensure QR codes work without animation

Animation Combinations
----------------------

Fade + Stagger
~~~~~~~~~~~~~~

Most popular combination creating a smooth wave reveal:

* Progressive module appearance
* Natural reading order flow
* Professional appearance

Fade + Pulse
~~~~~~~~~~~~

Draws attention to scanning areas:

* Static module fade-in
* Continuous finder emphasis
* Good for instructional contexts

All Effects
~~~~~~~~~~~

Rich animated experience:

* Wave-like module reveal
* Smooth opacity transitions
* Pulsing finder patterns
* Maximum visual interest

Limitations
-----------

* CSS-only implementation (no SMIL or Web Animations API)
* Index-based timing only (no custom per-module delays)
* Pulse effects limited to finder patterns
* No color transition animations
* No path morphing effects

Browser Compatibility
---------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Browser
     - Support Level
   * - Chrome 60+
     - Full support with hardware acceleration
   * - Firefox 55+
     - Full support with hardware acceleration
   * - Safari 11+
     - Full support with hardware acceleration
   * - Edge 79+
     - Full support with hardware acceleration
   * - IE 11
     - Graceful degradation to static QR code
   * - Mobile browsers
     - Full support with touch-optimized performance