globalThis.MODL = globalThis.MODL || {};

// Three.js is bundled ahead of this file and populates module.exports.
// Always bind this load's instance; a hot reload must not reuse the previous load's.
MODL.THREE = module.exports;
