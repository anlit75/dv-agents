import assert from "node:assert/strict";
import test from "node:test";

// The plugin intentionally keeps policy helpers private in v0.1.0.
// These tests exercise the same rules through a small extracted reference
// implementation so the expected security behavior is explicit.

const RTL_EXTENSIONS = [".v", ".sv", ".svh", ".vh", ".vhd", ".vhdl"];
const RTL_PATH_SEGMENTS = ["/rtl/", "/rtl_asic/", "/rtl_design/"];

function normalize(value) {
  return typeof value === "string" ? value.replaceAll("\\", "/").toLowerCase() : "";
}

function looksLikeRtlPath(value) {
  const p = normalize(value);
  return RTL_EXTENSIONS.some((x) => p.endsWith(x)) || RTL_PATH_SEGMENTS.some((x) => p.includes(x));
}

function blocked(tool, args) {
  if (["read", "edit", "write"].includes(tool)) {
    return looksLikeRtlPath(args?.filePath);
  }
  if (tool === "bash" || tool === "shell") {
    const command = args?.command ?? "";
    return /\.(?:v|sv|svh|vh|vhd|vhdl)\b|\/rtl\//i.test(command);
  }
  return false;
}

test("blocks direct RTL read", () => {
  assert.equal(blocked("read", { filePath: "/work/rtl/foo.sv" }), true);
});

test("allows normal DV files", () => {
  assert.equal(blocked("read", { filePath: "/work/dv/test/foo.py" }), false);
});

test("blocks shell commands that directly reference RTL", () => {
  assert.equal(blocked("bash", { command: "grep -n reset rtl/foo.sv" }), true);
});

test("allows normal shell commands", () => {
  assert.equal(blocked("bash", { command: "make test" }), false);
});
