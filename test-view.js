globalThis.MODL = globalThis.MODL || {};

MODL.obsidian = MODL.obsidian || require("obsidian");
MODL.TEST_VIEW_TYPE = "modl-test-view";

MODL.TestView = class extends MODL.obsidian.ItemView {
    constructor(leaf, plugin) {
        super(leaf);
        this.plugin = plugin;
        this.statusText = "Ready.";
        this.resizeHandler = null;
        this.animationFrame = 0;
        this.renderer = null;
        this.scene = null;
        this.camera = null;
        this.mesh = null;
        this.statusEl = null;
        this.viewportEl = null;
        this.orbitYaw = 0;
        this.orbitPitch = 0;
        this.orbitRadius = 3.2;
        this.orbitTarget = null;
        this.pointerState = null;
        this.gestureEl = null;
        this.pointerDownHandler = null;
        this.pointerMoveHandler = null;
        this.pointerUpHandler = null;
        this.resizeObserver = null;
        this.currentObjPath = "modl/obj/cube.obj";
        this.loadedTextures = [];
        this.loadedTextureUrls = [];
        this.loadedMaterial = null;
    }

    getViewType() {
        return MODL.TEST_VIEW_TYPE;
    }

    getDisplayText() {
        return "MODL Test";
    }

    onOpen() {
        this.render();
    }

    showSuccess(message) {
        this.statusText = message || "Success";
        if (this.statusEl) {
            this.statusEl.setText(this.sceneError || this.statusText);
        }
        this.ensureThreeScene().catch(error => this.reportSceneError(error));
    }

    // Keep a scene failure visible; a later success message must not hide it.
    reportSceneError(error) {
        const detail = error instanceof Error ? error.message : String(error);
        this.sceneError = `MODL test failed: ${detail}`;
        if (this.statusEl) {
            this.statusEl.setText(this.sceneError);
        }
        this.plugin.reportError("building the 3D test scene", error);
    }

    render() {
        const contentEl = this.contentEl;
        contentEl.empty();
        contentEl.style.padding = "0";
        contentEl.style.display = "flex";
        contentEl.style.flexDirection = "column";
        contentEl.style.height = "100%";
        contentEl.style.minHeight = "0";
        contentEl.style.overflow = "hidden";
        contentEl.style.position = "relative";

        this.viewportEl = contentEl.createEl("div");
        this.viewportEl.style.width = "100%";
        this.viewportEl.style.flex = "1";
        this.viewportEl.style.minHeight = "0";
        this.viewportEl.style.overflow = "hidden";
        this.viewportEl.style.background = "radial-gradient(circle at 50% 40%, #2f3b4f, #10151f)";

        this.statusEl = contentEl.createEl("div", {
            text: this.statusText
        });
        this.statusEl.style.position = "absolute";
        this.statusEl.style.left = "0.75em";
        this.statusEl.style.top = "0.75em";
        this.statusEl.style.padding = "0.35em 0.6em";
        this.statusEl.style.borderRadius = "999px";
        this.statusEl.style.background = "rgba(0, 0, 0, 0.45)";
        this.statusEl.style.color = "white";
        this.statusEl.style.fontSize = "0.85em";
        this.statusEl.style.zIndex = "3";

        this.ensureThreeScene().catch(error => this.reportSceneError(error));
    }

    getThree() {
        return MODL.THREE || null;
    }

    updateOrbitCamera() {
        if (!this.camera || !this.orbitTarget) {
            return;
        }

        const minPitch = -Math.PI * 0.48;
        const maxPitch = Math.PI * 0.48;
        this.orbitPitch = Math.max(minPitch, Math.min(maxPitch, this.orbitPitch));

        const radius = Math.max(1.2, Math.min(12, this.orbitRadius));
        this.orbitRadius = radius;

        const cosPitch = Math.cos(this.orbitPitch);
        const sinPitch = Math.sin(this.orbitPitch);
        const sinYaw = Math.sin(this.orbitYaw);
        const cosYaw = Math.cos(this.orbitYaw);

        const x = this.orbitTarget.x + radius * cosPitch * sinYaw;
        const y = this.orbitTarget.y + radius * sinPitch;
        const z = this.orbitTarget.z + radius * cosPitch * cosYaw;

        this.camera.position.set(x, y, z);
        this.camera.lookAt(this.orbitTarget);
    }

    setupMobileOrbitControls() {
        if (!this.gestureEl || !this.camera) {
            return;
        }

        const pointers = new Map();
        let lastDistance = 0;
        const rotateSpeed = 0.01;
        const zoomSpeed = 0.01;

        const pointerIds = () => [...pointers.keys()];
        const getDistance = () => {
            const ids = pointerIds();
            if (ids.length < 2) {
                return 0;
            }
            const a = pointers.get(ids[0]);
            const b = pointers.get(ids[1]);
            if (!a || !b) {
                return 0;
            }
            return Math.hypot(b.x - a.x, b.y - a.y);
        };

        this.pointerDownHandler = event => {
            const point = { x: event.clientX, y: event.clientY, prevX: event.clientX, prevY: event.clientY };
            pointers.set(event.pointerId, point);
            this.gestureEl.setPointerCapture(event.pointerId);

            if (pointers.size === 2) {
                lastDistance = getDistance();
            }

            event.preventDefault();
            event.stopPropagation();
        };

        this.pointerMoveHandler = event => {
            const point = pointers.get(event.pointerId);
            if (!point) {
                return;
            }

            point.prevX = point.x;
            point.prevY = point.y;
            point.x = event.clientX;
            point.y = event.clientY;

            if (pointers.size === 1) {
                const dx = point.x - point.prevX;
                const dy = point.y - point.prevY;
                this.orbitYaw -= dx * rotateSpeed;
                this.orbitPitch -= dy * rotateSpeed;
                this.updateOrbitCamera();
            } else if (pointers.size >= 2) {
                const distance = getDistance();
                if (lastDistance > 0 && distance > 0) {
                    const delta = distance - lastDistance;
                    this.orbitRadius -= delta * zoomSpeed;
                    this.updateOrbitCamera();
                }
                lastDistance = distance;
            }

            event.preventDefault();
            event.stopPropagation();
        };

        this.pointerUpHandler = event => {
            pointers.delete(event.pointerId);
            if (this.gestureEl.hasPointerCapture(event.pointerId)) {
                this.gestureEl.releasePointerCapture(event.pointerId);
            }

            if (pointers.size < 2) {
                lastDistance = 0;
            }

            event.preventDefault();
            event.stopPropagation();
        };

        this.gestureEl.addEventListener("pointerdown", this.pointerDownHandler, { passive: false });
        this.gestureEl.addEventListener("pointermove", this.pointerMoveHandler, { passive: false });
        this.gestureEl.addEventListener("pointerup", this.pointerUpHandler, { passive: false });
        this.gestureEl.addEventListener("pointercancel", this.pointerUpHandler, { passive: false });
        this.pointerState = pointers;
    }

    syncRendererSizeToViewport() {
        if (!this.renderer || !this.camera || !this.viewportEl) {
            return;
        }

        const nextWidth = Math.max(1, this.viewportEl.clientWidth || 320);
        const nextHeight = Math.max(1, this.viewportEl.clientHeight || 240);

        this.camera.aspect = nextWidth / nextHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(nextWidth, nextHeight, false);
    }

    dirnameOf(path) {
        const normalized = String(path || "").replace(/\\/g, "/");
        const index = normalized.lastIndexOf("/");
        return index === -1 ? "" : normalized.slice(0, index + 1);
    }

    joinPath(dir, name) {
        const left = String(dir || "").replace(/\\/g, "/");
        const right = String(name || "").replace(/^\.?\//, "").replace(/\\/g, "/");
        return `${left}${right}`;
    }

    parseObjTextToGeometry(THREE, text) {
        const raw = String(text || "").replace(/\r/g, "");
        const lines = raw.split("\n");

        const positions = [];
        const texcoords = [];
        const normals = [];

        const outPositions = [];
        const outNormals = [];
        const outUvs = [];

        const parseVertexToken = token => {
            const parts = String(token || "").split("/");
            const vi = Number(parts[0]);
            const ti = parts.length > 1 && parts[1] !== "" ? Number(parts[1]) : NaN;
            const ni = parts.length > 2 && parts[2] !== "" ? Number(parts[2]) : NaN;

            const vIndex = Number.isFinite(vi) ? (vi > 0 ? vi - 1 : positions.length + vi) : -1;
            const tIndex = Number.isFinite(ti) ? (ti > 0 ? ti - 1 : texcoords.length + ti) : -1;
            const nIndex = Number.isFinite(ni) ? (ni > 0 ? ni - 1 : normals.length + ni) : -1;

            return { vIndex, tIndex, nIndex };
        };

        const pushVertex = token => {
            const ref = parseVertexToken(token);
            const p = positions[ref.vIndex];
            if (!p) {
                throw new Error(`OBJ parse error: missing position index in token '${token}'.`);
            }

            outPositions.push(p[0], p[1], p[2]);

            const uv = texcoords[ref.tIndex] || [0, 0];
            outUvs.push(uv[0], uv[1]);

            const n = normals[ref.nIndex] || [0, 0, 1];
            outNormals.push(n[0], n[1], n[2]);
        };

        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith("#")) {
                continue;
            }

            if (trimmed.startsWith("v ")) {
                const parts = trimmed.split(/\s+/);
                positions.push([
                    Number(parts[1] || 0),
                    Number(parts[2] || 0),
                    Number(parts[3] || 0)
                ]);
                continue;
            }

            if (trimmed.startsWith("vt ")) {
                const parts = trimmed.split(/\s+/);
                texcoords.push([
                    Number(parts[1] || 0),
                    Number(parts[2] || 0)
                ]);
                continue;
            }

            if (trimmed.startsWith("vn ")) {
                const parts = trimmed.split(/\s+/);
                normals.push([
                    Number(parts[1] || 0),
                    Number(parts[2] || 0),
                    Number(parts[3] || 1)
                ]);
                continue;
            }

            if (trimmed.startsWith("f ")) {
                const parts = trimmed.split(/\s+/).slice(1);
                if (parts.length < 3) {
                    continue;
                }

                for (let i = 1; i < parts.length - 1; i++) {
                    pushVertex(parts[0]);
                    pushVertex(parts[i]);
                    pushVertex(parts[i + 1]);
                }
            }
        }

        if (outPositions.length === 0) {
            throw new Error("OBJ parse error: no face vertices were produced.");
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(outPositions, 3)
        );
        geometry.setAttribute(
            "normal",
            new THREE.Float32BufferAttribute(outNormals, 3)
        );
        geometry.setAttribute(
            "uv",
            new THREE.Float32BufferAttribute(outUvs, 2)
        );
        geometry.computeBoundingSphere();
        return geometry;
    }

    parseObjMeta(text) {
        const raw = String(text || "").replace(/\r/g, "");
        const lines = raw.split("\n");
        let mtllib = "";
        let usemtl = "";

        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith("#")) {
                continue;
            }

            if (!mtllib && trimmed.toLowerCase().startsWith("mtllib ")) {
                mtllib = trimmed.slice(7).trim();
                continue;
            }

            if (!usemtl && trimmed.toLowerCase().startsWith("usemtl ")) {
                usemtl = trimmed.slice(7).trim();
            }
        }

        return { mtllib, usemtl };
    }

    parseMtlText(text) {
        const raw = String(text || "").replace(/\r/g, "");
        const lines = raw.split("\n");
        const result = {
            materialName: "",
            mapKd: "",
            mapBump: ""
        };

        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith("#")) {
                continue;
            }

            const lower = trimmed.toLowerCase();
            if (!result.materialName && lower.startsWith("newmtl ")) {
                result.materialName = trimmed.slice(7).trim();
                continue;
            }
            if (!result.mapKd && lower.startsWith("map_kd ")) {
                result.mapKd = trimmed.slice(7).trim();
                continue;
            }
            if (!result.mapBump && (lower.startsWith("map_bump ") || lower.startsWith("bump "))) {
                const value = lower.startsWith("bump ") ? trimmed.slice(5) : trimmed.slice(9);
                result.mapBump = value.trim();
            }
        }

        return result;
    }

    async loadTextureFromVaultPath(THREE, path) {
        const file = this.app.vault.getAbstractFileByPath(path);
        if (!file || !file.extension) {
            return null;
        }

        const binary = await this.app.vault.readBinary(file);
        const blob = new Blob([binary], { type: "image/png" });
        const objectUrl = URL.createObjectURL(blob);

        const texture = await new Promise((resolve, reject) => {
            const loader = new THREE.TextureLoader();
            loader.load(
                objectUrl,
                loaded => resolve(loaded),
                undefined,
                error => reject(error || new Error(`Texture load failed: ${path}`))
            );
        });

        texture.colorSpace = THREE.SRGBColorSpace || texture.colorSpace;
        texture.needsUpdate = true;

        this.loadedTextureUrls.push(objectUrl);
        this.loadedTextures.push(texture);
        return texture;
    }

    async loadMaterialForObj(THREE, objPath, objText) {
        const meta = this.parseObjMeta(objText);
        if (!meta.mtllib) {
            return null;
        }

        const objDir = this.dirnameOf(objPath);
        const mtlPath = this.joinPath(objDir, meta.mtllib);
        const mtlFile = this.app.vault.getAbstractFileByPath(mtlPath);
        if (!mtlFile || !mtlFile.extension) {
            return null;
        }

        const mtlText = await this.app.vault.cachedRead(mtlFile);
        const parsedMtl = this.parseMtlText(mtlText);

        let map = null;
        let normalMap = null;

        if (parsedMtl.mapKd) {
            map = await this.loadTextureFromVaultPath(
                THREE,
                this.joinPath(this.dirnameOf(mtlPath), parsedMtl.mapKd)
            );
        }

        if (parsedMtl.mapBump) {
            normalMap = await this.loadTextureFromVaultPath(
                THREE,
                this.joinPath(this.dirnameOf(mtlPath), parsedMtl.mapBump)
            );
        }

        const material = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            map: map || null,
            normalMap: normalMap || null,
            roughness: 0.9,
            metalness: 0.0
        });

        this.loadedMaterial = material;
        return material;
    }

    async loadObjGeometry(THREE, objPath) {
        const path = String(objPath || "").trim();
        if (!path) {
            throw new Error("OBJ path was empty.");
        }

        const file = this.app.vault.getAbstractFileByPath(path);
        if (!file || !file.extension) {
            throw new Error(`OBJ not found: ${path}`);
        }

        const text = await this.app.vault.cachedRead(file);
        return {
            geometry: this.parseObjTextToGeometry(THREE, text),
            text
        };
    }

    async ensureThreeScene() {
        if (this.renderer || !this.viewportEl) {
            return;
        }

        const THREE = this.getThree();
        if (!THREE) {
            if (this.statusEl) {
                this.statusEl.setText("MODL test failed: Three.js not loaded. Run modl/build.sh to vendor and bundle Three.js.");
            }
            return;
        }

        const width = Math.max(1, this.viewportEl.clientWidth || 320);
        const height = Math.max(1, this.viewportEl.clientHeight || 240);

        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
        this.orbitYaw = 0;
        this.orbitPitch = 0;
        this.orbitRadius = 3.2;
        this.orbitTarget = new THREE.Vector3(0, 0, 0);

        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
        this.renderer.setSize(width, height, false);
        this.renderer.domElement.style.width = "100%";
        this.renderer.domElement.style.height = "100%";
        this.renderer.domElement.style.display = "block";
        this.renderer.domElement.style.touchAction = "none";

        this.viewportEl.empty();
        this.viewportEl.appendChild(this.renderer.domElement);
        this.gestureEl = this.renderer.domElement;

        const ambient = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0xffffff, 0.9);
        keyLight.position.set(2, 3, 4);
        this.scene.add(keyLight);

        const loadedObj = await this.loadObjGeometry(THREE, this.currentObjPath);
        const geometry = loadedObj.geometry;
        const material = await this.loadMaterialForObj(THREE, this.currentObjPath, loadedObj.text)
            || new THREE.MeshNormalMaterial();
        this.mesh = new THREE.Mesh(geometry, material);
        this.scene.add(this.mesh);

        this.updateOrbitCamera();
        this.setupMobileOrbitControls();

        this.resizeHandler = () => {
            this.syncRendererSizeToViewport();
        };

        window.addEventListener("resize", this.resizeHandler);

        if (typeof ResizeObserver !== "undefined") {
            this.resizeObserver = new ResizeObserver(() => {
                this.syncRendererSizeToViewport();
            });
            this.resizeObserver.observe(this.viewportEl);
        }

        this.syncRendererSizeToViewport();

        const tick = () => {
            if (!this.renderer || !this.scene || !this.camera || !this.mesh) {
                return;
            }

            this.mesh.rotation.x += 0.01;
            this.mesh.rotation.y += 0.015;
            this.renderer.render(this.scene, this.camera);
            this.animationFrame = window.requestAnimationFrame(tick);
        };

        tick();

        if (this.statusEl) {
            this.statusEl.setText(this.statusText || "MODL test success (OBJ + material).");
        }
    }

    teardownThreeScene() {
        if (this.animationFrame) {
            window.cancelAnimationFrame(this.animationFrame);
            this.animationFrame = 0;
        }

        if (this.resizeHandler) {
            window.removeEventListener("resize", this.resizeHandler);
            this.resizeHandler = null;
        }

        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
            this.resizeObserver = null;
        }

        if (this.gestureEl) {
            if (this.pointerDownHandler) {
                this.gestureEl.removeEventListener("pointerdown", this.pointerDownHandler);
            }
            if (this.pointerMoveHandler) {
                this.gestureEl.removeEventListener("pointermove", this.pointerMoveHandler);
            }
            if (this.pointerUpHandler) {
                this.gestureEl.removeEventListener("pointerup", this.pointerUpHandler);
                this.gestureEl.removeEventListener("pointercancel", this.pointerUpHandler);
            }
        }

        this.pointerState = null;
        this.gestureEl = null;
        this.pointerDownHandler = null;
        this.pointerMoveHandler = null;
        this.pointerUpHandler = null;

        if (this.mesh) {
            if (this.mesh.geometry && typeof this.mesh.geometry.dispose === "function") {
                this.mesh.geometry.dispose();
            }
            if (this.mesh.material) {
                if (Array.isArray(this.mesh.material)) {
                    this.mesh.material.forEach(item => item && typeof item.dispose === "function" && item.dispose());
                } else if (typeof this.mesh.material.dispose === "function") {
                    this.mesh.material.dispose();
                }
            }
            this.mesh = null;
        }

        if (this.loadedMaterial && typeof this.loadedMaterial.dispose === "function") {
            this.loadedMaterial.dispose();
        }
        this.loadedMaterial = null;

        for (const texture of this.loadedTextures) {
            if (texture && typeof texture.dispose === "function") {
                texture.dispose();
            }
        }
        this.loadedTextures = [];

        for (const url of this.loadedTextureUrls) {
            try {
                URL.revokeObjectURL(url);
            } catch (error) {}
        }
        this.loadedTextureUrls = [];

        if (this.renderer) {
            if (typeof this.renderer.dispose === "function") {
                this.renderer.dispose();
            }
            this.renderer = null;
        }

        this.scene = null;
        this.camera = null;
    }

    onClose() {
        this.teardownThreeScene();
        this.contentEl.empty();
    }
};
