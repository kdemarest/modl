globalThis.MODL = globalThis.MODL || {};

(function bindThreeIntoBB() {
    if (MODL.THREE) {
        return;
    }

    if (typeof globalThis !== "undefined" && globalThis.THREE) {
        MODL.THREE = globalThis.THREE;
        return;
    }

    if (
        typeof module !== "undefined" &&
        module.exports &&
        typeof module.exports === "object" &&
        typeof module.exports.Scene === "function"
    ) {
        MODL.THREE = module.exports;
    }
})();
