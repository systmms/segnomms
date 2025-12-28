.. _naming-conventions:

Boolean Naming Conventions
==========================

This guide documents the naming conventions for boolean configuration options in SegnoMMS.
Following these patterns ensures API consistency and improves developer experience.

Overview
--------

SegnoMMS uses four distinct naming patterns for boolean options, each serving a specific purpose:

.. list-table:: Boolean Naming Patterns
   :widths: 20 30 50
   :header-rows: 1

   * - Pattern
     - When to Use
     - Examples
   * - Bare name
     - Segno-inherited concepts
     - ``eci``, ``boost_error``, ``micro``
   * - ``*_enabled`` suffix
     - State booleans (feature toggles)
     - ``centerpiece_enabled``, ``phase1.enabled``
   * - ``use_*`` prefix
     - Algorithm/strategy selection
     - ``use_marching_squares``, ``use_cluster_rendering``
   * - Bare name
     - UI interaction behaviors
     - ``interactive``, ``tooltips``

Pattern Details
---------------

Bare Names for Segno Concepts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Options inherited from or directly related to Segno's API use bare names without
prefixes or suffixes. This maintains compatibility with upstream conventions.

.. code-block:: python

   # Correct - Segno-inherited concepts
   qr.save("output.svg", kind="svg",
           eci=True,          # Extended Channel Interpretation
           boost_error=True,  # Error correction boost
           micro=False)       # Micro QR mode

``*_enabled`` Suffix for State Booleans
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

State booleans that toggle features on/off use the ``*_enabled`` suffix.
This clearly indicates the option controls whether something is active.

.. code-block:: python

   # Correct - state toggles
   config = RenderingConfig(
       centerpiece_enabled=True,  # Enable centerpiece/logo area
       safe_mode_enabled=True,    # Enable safe rendering fallbacks
   )

   # Phase configurations use nested 'enabled' field
   config = RenderingConfig(
       phase1=Phase1Config(enabled=True),
       phase2=Phase2Config(enabled=True),
   )

``use_*`` Prefix for Strategy Selection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Options that select between algorithms or strategies use the ``use_*`` prefix.
This indicates a choice between implementation approaches.

.. code-block:: python

   # Correct - strategy selection
   config = RenderingConfig(
       use_marching_squares=True,    # Use marching squares for contours
       use_cluster_rendering=True,   # Use cluster-based rendering
       use_enhanced_shapes=False,    # Use enhanced shape detection
   )

Bare Names for UI Behaviors
^^^^^^^^^^^^^^^^^^^^^^^^^^^

UI interaction behaviors that are not toggles use bare descriptive names.

.. code-block:: python

   # Correct - UI behaviors
   qr.save("output.svg", kind="svg",
           interactive=True,   # Enable interactive SVG features
           tooltips=True)      # Show tooltips on hover

Deprecated Pattern
------------------

The ``enable_*`` prefix pattern is **deprecated** and should not be used in new code.
This pattern uses an action verb (enable) rather than a state descriptor, which is
less clear than the ``*_enabled`` suffix.

.. code-block:: python

   # Deprecated - avoid in new code
   enable_caching=True        # Use 'caching_enabled' instead
   enable_validation=True     # Use 'validation_enabled' instead

Existing options using this pattern will continue to work but should be migrated
when making other changes to the codebase.

Rationale
---------

This hybrid approach balances several concerns:

1. **Segno Compatibility**: Bare names for Segno concepts maintain consistency with
   upstream library conventions

2. **Clarity**: The ``*_enabled`` suffix clearly distinguishes state toggles from
   other boolean types

3. **Discoverability**: Consistent patterns help developers predict option names
   when using IDE autocompletion

4. **Ecosystem Alignment**: The Python QR/image ecosystem (Segno, qrcode, Pillow)
   generally prefers concise naming patterns

For Developers
--------------

When adding new boolean configuration options:

1. **Check if the concept is Segno-inherited** - if so, use bare name
2. **Is it a feature toggle?** - use ``*_enabled`` suffix
3. **Is it choosing between implementations?** - use ``use_*`` prefix
4. **Is it a UI behavior?** - use bare descriptive name
5. **Avoid** the deprecated ``enable_*`` prefix pattern

Run the naming audit to verify compliance:

.. code-block:: bash

   make audit-naming

See Also
--------

* :doc:`/api/config` - Configuration API reference
* :doc:`/migration/deprecated-options` - Migration guide for deprecated options
