unit("plugin", ["three"], () => {
globalThis.MODL = globalThis.MODL || {};

MODL.obsidian = MODL.obsidian || require("obsidian");

MODL.LOG_PATH = "modl/modl.log";
MODL.LAST_ERROR_PATH = "modl/_lastErr.log";
MODL.CODE_MAP_PATH = "modl/runtime-code-map.json";

MODL.Plugin = class extends MODL.obsidian.Plugin {
    async onload() {
        this.errorModal = null;
        await this.appendRunLog();

        this.registerView(
            MODL.TEST_VIEW_TYPE,
            leaf => new MODL.TestView(leaf, this)
        );

        this.addCommand({
            id: "modl-test",
            name: "test",
            callback: async () => {
                try {
                    await this.runTestAction();
                } catch (error) {
                    this.reportError("running the test command", error);
                }
            }
        });
    }

    async onunload() {
        if (this.errorModal) {
            this.errorModal.close();
            this.errorModal = null;
        }
        for (const leaf of this.app.workspace.getLeavesOfType(MODL.TEST_VIEW_TYPE)) {
            leaf.detach();
        }
        // Drop shared state so a hot reload starts from a clean namespace.
        delete globalThis.MODL;
    }

    async appendLog(text) {
        const adapter = this.app.vault.adapter;

        if (await adapter.exists(MODL.LOG_PATH)) {
            await adapter.append(MODL.LOG_PATH, text);
        } else {
            await adapter.write(MODL.LOG_PATH, text);
        }
    }

    async appendRunLog() {
        await this.appendLog(`\n${new Date().toISOString()}\n\n`);
    }

    extractBundlePositionFromErrorDetail(detail) {
        // Desktop stacks name the bundle file; mobile stacks name the plugin.
        const match = /(?:main\.js|plugin:modl):(\d+):(\d+)/.exec(String(detail || ""));

        if (!match) {
            return null;
        }

        return {
            line: Number(match[1]),
            column: Number(match[2])
        };
    }

    async loadRuntimeCodeMap() {
        if (this.runtimeCodeMapLoaded) {
            return this.runtimeCodeMap;
        }

        this.runtimeCodeMapLoaded = true;
        this.runtimeCodeMap = null;

        const adapter = this.app.vault.adapter;

        try {
            if (!(await adapter.exists(MODL.CODE_MAP_PATH))) {
                return null;
            }

            const parsed = JSON.parse(await adapter.read(MODL.CODE_MAP_PATH));

            if (!parsed || !Array.isArray(parsed.entries)) {
                return null;
            }

            const entries = parsed.entries
                .map(entry => ({
                    sourcePath: typeof entry?.sourcePath === "string" ? entry.sourcePath : "",
                    sourceStartLine: Number(entry?.sourceStartLine),
                    bundleStartLine: Number(entry?.bundleStartLine),
                    bundleEndLine: Number(entry?.bundleEndLine)
                }))
                .filter(entry =>
                    entry.sourcePath &&
                    Number.isFinite(entry.sourceStartLine) &&
                    Number.isFinite(entry.bundleStartLine) &&
                    Number.isFinite(entry.bundleEndLine)
                )
                .sort((left, right) => left.bundleStartLine - right.bundleStartLine);

            this.runtimeCodeMap = {
                path: MODL.CODE_MAP_PATH,
                entries
            };

            return this.runtimeCodeMap;
        } catch (mapError) {
            console.error("MODL could not load runtime-code-map.json", mapError);
            return null;
        }
    }

    resolveSourceLocationFromBundle(bundleLine, bundleColumn, codeMap) {
        if (!codeMap || !Array.isArray(codeMap.entries)) {
            return null;
        }

        for (const entry of codeMap.entries) {
            if (bundleLine < entry.bundleStartLine || bundleLine > entry.bundleEndLine) {
                continue;
            }

            return {
                sourcePath: entry.sourcePath,
                sourceLine: entry.sourceStartLine + (bundleLine - entry.bundleStartLine),
                sourceColumn: bundleColumn,
                mapPath: codeMap.path
            };
        }

        return null;
    }

    async writeLastRuntimeError(context, detail, now) {
        const bundlePosition = this.extractBundlePositionFromErrorDetail(detail);
        let bundleLocation = "Bundle location: unavailable";
        let sourceLocation = "Source location: unresolved";

        if (bundlePosition) {
            bundleLocation = `Bundle location: .obsidian/plugins/modl/main.js:${bundlePosition.line}:${bundlePosition.column}`;
            const codeMap = await this.loadRuntimeCodeMap();
            const source = this.resolveSourceLocationFromBundle(
                bundlePosition.line,
                bundlePosition.column,
                codeMap
            );

            if (source) {
                sourceLocation = `Source location: ${source.sourcePath}:${source.sourceLine}:${source.sourceColumn} (map: ${source.mapPath})`;
            } else if (codeMap) {
                sourceLocation = `Source location: unresolved (map: ${codeMap.path})`;
            }
        }

        const lastErrorPayload = [
            "MODL failure",
            "Project: modl",
            "Error type: runtime",
            `Generated: ${now}`,
            `Operation: ${context}`,
            bundleLocation,
            sourceLocation,
            "",
            detail
        ].join("\n");

        await this.app.vault.adapter.write(MODL.LAST_ERROR_PATH, `${lastErrorPayload}\n`);
    }

    reportError(context, error) {
        const detail = error instanceof Error
            ? error.stack || error.message
            : String(error);
        const now = new Date().toISOString();
        console.error(`MODL ${context} failed: ${detail}`, error);

        this.appendLog(`ERROR [${now}] ${context}\n${detail}\n\n`).catch(logError => {
            console.error("MODL could not write modl.log", logError);
        });

        this.writeLastRuntimeError(context, detail, now).catch(writeError => {
            console.error("MODL could not write _lastErr.log", writeError);
        });

        if (this.errorModal) {
            this.errorModal.setError(context, error);
            return;
        }

        this.errorModal = new MODL.ErrorModal(this.app, this, context, error);
        this.errorModal.open();
    }

    async openTestView() {
        const workspace = this.app.workspace;
        const existingLeaves = workspace.getLeavesOfType(MODL.TEST_VIEW_TYPE);
        const leaf = existingLeaves[0] || workspace.getLeaf("tab");

        if (!existingLeaves[0]) {
            await leaf.setViewState({
                type: MODL.TEST_VIEW_TYPE,
                active: true
            });
        }

        await workspace.revealLeaf(leaf);

        if (!(leaf.view instanceof MODL.TestView)) {
            throw new Error(`Test view leaf holds a ${leaf.view.getViewType()} view.`);
        }

        return leaf.view;
    }

    async runTestAction() {
        const view = await this.openTestView();
        const message = "MODL test success.";
        view.showSuccess(message);

        new MODL.obsidian.Notice(message);
    }
};

module.exports = MODL.Plugin;
});
