unit("three", [], () => {
globalThis.MODL = globalThis.MODL || {};

// Three.js (vendor, bundled before any unit runs) populates module.exports.
// Always bind this load's instance; a hot reload must not reuse the previous load's.
MODL.THREE = module.exports;
});
