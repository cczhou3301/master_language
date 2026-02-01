import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig(function (_a) {
    var mode = _a.mode;
    return ({
        plugins: [react()],
        server: { port: 5173, host: true },
        build: { outDir: "dist", sourcemap: mode !== "production" },
    });
});
