import "@testing-library/jest-dom";
import { vi } from "vitest";

if (!globalThis.fetch) {
  globalThis.fetch = vi.fn(async () => ({
    ok: true,
    status: 200,
    text: async () => JSON.stringify({ airports: [], notifications: [] }),
  }));
}
