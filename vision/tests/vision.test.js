"use strict";
/**
 * vision.js 纯函数确定性测试（node:test，无需网络/API Key）。
 * 运行: npm test  /  node --test tests/
 */
const { test } = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const vision = require("../vision.js");

function withEnv(overrides, fn) {
  const prev = {};
  for (const k of Object.keys(overrides)) {
    prev[k] = process.env[k];
    if (overrides[k] === undefined) delete process.env[k];
    else process.env[k] = overrides[k];
  }
  try { return fn(); }
  finally {
    for (const k of Object.keys(overrides)) {
      if (prev[k] === undefined) delete process.env[k];
      else process.env[k] = prev[k];
    }
  }
}

test("parseArgs: 位置参数 + 默认提示", () => {
  const a = vision.parseArgs(["a.png"]);
  assert.equal(a.imageSource, "a.png");
  assert.equal(a.isUrl, false);
  assert.equal(a.prompt, "请详细描述这张图片的内容。");
});

test("parseArgs: 多词 prompt 合并为一句", () => {
  const a = vision.parseArgs(["a.png", "这是", "一只猫"]);
  assert.equal(a.prompt, "这是 一只猫");
});

test("parseArgs: --url 模式", () => {
  const a = vision.parseArgs(["--url", "https://x/a.png", "描述一下"]);
  assert.equal(a.isUrl, true);
  assert.equal(a.imageSource, "https://x/a.png");
  assert.equal(a.prompt, "描述一下");
});

test("parseArgs: 无参数时 imageSource 为空", () => {
  assert.equal(vision.parseArgs([]).imageSource, "");
});

test("parseArgs: --url 后缺值不吞掉参数", () => {
  const a = vision.parseArgs(["--url"]);
  assert.equal(a.imageSource, "");
});

test("resolveModels: 默认兜底列表", () => {
  withEnv({ VISION_MODELS: undefined, VISION_MODEL: undefined }, () => {
    assert.deepEqual(vision.resolveModels(), vision.DEFAULT_MODELS);
  });
});

test("resolveModels: VISION_MODELS 逗号分隔覆盖", () => {
  withEnv({ VISION_MODELS: "a, b, c", VISION_MODEL: "x" }, () => {
    assert.deepEqual(vision.resolveModels(), ["a", "b", "c"]);
  });
});

test("resolveModels: 仅 VISION_MODEL 时用单模型", () => {
  withEnv({ VISION_MODELS: undefined, VISION_MODEL: "single-model" }, () => {
    assert.deepEqual(vision.resolveModels(), ["single-model"]);
  });
});

test("resolveImageUrl: URL 原样返回", () => {
  assert.equal(vision.resolveImageUrl("https://x/a.png", true), "https://x/a.png");
});

test("resolveImageUrl: 本地文件转 base64 data URL", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "vision-test-"));
  const f = path.join(dir, "t.png");
  const bytes = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  fs.writeFileSync(f, bytes);
  try {
    const url = vision.resolveImageUrl(f, false);
    assert.ok(url.startsWith("data:image/png;base64,"), `prefix 异常: ${url.slice(0, 30)}`);
    assert.equal(url.split(",")[1], bytes.toString("base64"));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("resolveImageUrl: 不存在的文件抛错", () => {
  assert.throws(() => vision.resolveImageUrl("C:/no/such/file.png", false), /文件不存在/);
});

test("resolveImageUrl: 超过 10MB 的图片抛错", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "vision-test-"));
  const f = path.join(dir, "big.png");
  const fd = fs.openSync(f, "w");
  fs.ftruncateSync(fd, 10 * 1024 * 1024 + 1);
  fs.closeSync(fd);
  try {
    assert.throws(() => vision.resolveImageUrl(f, false), /图片过大/);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});