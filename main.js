globalThis.MODL = globalThis.MODL || {};

MODL.obsidian = MODL.obsidian || require("obsidian");

MODL.Plugin = class extends MODL.obsidian.Plugin {
    async onload() {
        this.registerView(
            MODL.TEST_VIEW_TYPE,
            leaf => new MODL.TestView(leaf, this)
        );

        this.addCommand({
            id: "modl-test",
            name: "test",
            callback: async () => {
                await this.runTestAction();
            }
        });
    }

    async onunload() {
        for (const leaf of this.app.workspace.getLeavesOfType(MODL.TEST_VIEW_TYPE)) {
            leaf.detach();
        }
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

        if (leaf.view instanceof MODL.TestView) {
            return leaf.view;
        }

        return null;
    }

    async runTestAction() {
        const view = await this.openTestView();
        const message = "MODL test success.";

        if (view && typeof view.showSuccess === "function") {
            view.showSuccess(message);
        }

        new MODL.obsidian.Notice(message);
    }
};

module.exports = MODL.Plugin;
