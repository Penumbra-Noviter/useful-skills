#!/usr/bin/env node
/**
 * 识图 + 生图脚本 — 调用千问 VL 模型识图，或 SiliconFlow 免费生图。
 *
 * 识图用法:
 *   node vision.js <图片路径> [问题]
 *   node vision.js --url <图片链接> [问题]
 *
 * 生图用法:
 *   node vision.js --generate "<英文提示词>" [选项]
 *     选项:
 *       --model <模型>  默认 kolors (kolors, qwen, zimage, flux)
 *       --width <宽>    默认 1024
 *       --height <高>   默认 1024
 *       --output <路径> 输出文件路径
 *
 * 依赖:
 *   npm install dotenv (可选，如果有 .env 文件)
 *   DASHSCOPE_API_KEY 环境变量 或 同目录 .env 文件（仅识图需要）
 *   SILICONFLOW_API_KEY 环境变量 或 同目录 .env 文件（仅生图需要，免费在 cloud.siliconflow.cn 获取）
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

// 尝试加载 .env（先找当前目录，再找脚本所在目录）
try { require("dotenv").config(); } catch {}
try { require("dotenv").config({ path: path.resolve(__dirname, ".env") }); } catch {}

const BASE_URL = process.env.DASHSCOPE_BASE_URL || "https://dashscope.aliyuncs.com/compatible-mode/v1";
// 安全：API Key 只从环境变量或同目录 .env 读取，禁止硬编码进代码
const API_KEY = process.env.DASHSCOPE_API_KEY || "";
const MODEL = process.env.VISION_MODEL || "qwen3.7-flash";
const SILICONFLOW_API_KEY = process.env.SILICONFLOW_API_KEY || "";
const SILICONFLOW_BASE_URL = process.env.SILICONFLOW_BASE_URL || "https://api.siliconflow.cn/v1";

// SiliconFlow 模型映射
const SF_MODELS = {
  flux: "black-forest-labs/FLUX.1-dev",
  kolors: "Kwai-Kolors/Kolors",
  qwen: "Qwen/Qwen-Image",
  zimage: "Tongyi-MAI/Z-Image-Turbo",
};

function parseArgs() {
  const argv = process.argv.slice(2);
  let imageSource = "", prompt = "", isUrl = false, isGenerate = false;
  let model = "flux", width = 1024, height = 1024, seed = null, output = "";

  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--generate") {
      isGenerate = true;
    } else if (argv[i] === "--url" && argv[i + 1]) {
      isUrl = true;
      imageSource = argv[++i];
    } else if (argv[i] === "--model" && argv[i + 1]) {
      model = argv[++i];
    } else if (argv[i] === "--width" && argv[i + 1]) {
      width = parseInt(argv[++i], 10) || 1024;
    } else if (argv[i] === "--height" && argv[i + 1]) {
      height = parseInt(argv[++i], 10) || 1024;
    } else if (argv[i] === "--seed" && argv[i + 1]) {
      seed = parseInt(argv[++i], 10);
    } else if (argv[i] === "--output" && argv[i + 1]) {
      output = argv[++i];
    } else if (!argv[i].startsWith("--")) {
      if (isGenerate) {
        prompt = prompt ? prompt + " " + argv[i] : argv[i];
      } else if (!imageSource) {
        imageSource = argv[i];
      } else {
        prompt = prompt ? prompt + " " + argv[i] : argv[i];
      }
    }
  }
  if (!isGenerate && !prompt) prompt = "请详细描述这张图片的内容。";
  return { imageSource, prompt, isUrl, isGenerate, model, width, height, seed, output };
}

function resolveImageUrl(source, isUrl) {
  if (isUrl) return source;
  const resolved = path.resolve(source);
  if (!fs.existsSync(resolved)) throw new Error(`文件不存在: ${resolved}`);
  const ext = path.extname(resolved).toLowerCase().replace(".", "");
  const mimeMap = { jpg: "jpeg", jpeg: "jpeg", png: "png", gif: "gif", webp: "webp", bmp: "bmp" };
  const data = fs.readFileSync(resolved);
  return `data:image/${mimeMap[ext] || "jpeg"};base64,${data.toString("base64")}`;
}

function request(payload) {
  const url = new URL(BASE_URL.replace(/\/?$/, "/") + "chat/completions");
  const body = JSON.stringify(payload);
  const transport = url.protocol === "https:" ? https : http;

  return new Promise((resolve, reject) => {
    const req = transport.request(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
    }, (res) => {
      let data = "";
      res.on("data", (c) => data += c);
      res.on("end", () => {
        if (res.statusCode >= 400) return reject(new Error(`API ${res.statusCode}: ${data.slice(0, 300)}`));
        try {
          resolve(JSON.parse(data)?.choices?.[0]?.message?.content || data);
        } catch { resolve(data); }
      });
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

/**
 * 调用 SiliconFlow API 免费生图，下载图片到本地。
 * 需要设置 SILICONFLOW_API_KEY（免费在 cloud.siliconflow.cn 获取）。
 * 支持 OpenAI 兼容格式，默认使用 FLUX.1-dev 模型。
 * @param {string} prompt - 英文提示词
 * @param {{ width: number, height: number, model: string, output: string }} opts
 * @returns {Promise<{ path: string }>}
 */
function generateImage(prompt, opts) {
  const sfModel = SF_MODELS[opts.model] || SF_MODELS.flux;
  const url = `${SILICONFLOW_BASE_URL.replace(/\/?$/, "")}/image/generations`;
  const output = opts.output || path.join(process.cwd(), `generated_${Date.now()}.png`);
  const body = JSON.stringify({
    model: sfModel,
    prompt: prompt,
    n: 1,
    size: `${opts.width}x${opts.height}`,
  });

  return new Promise((resolve, reject) => {
    const req = https.request(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${SILICONFLOW_API_KEY}`,
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
    }, (res) => {
      let data = "";
      res.on("data", (c) => data += c);
      res.on("end", () => {
        if (res.statusCode >= 400) {
          return reject(new Error(`API ${res.statusCode}: ${data.slice(0, 300)}`));
        }
        try {
          const parsed = JSON.parse(data);
          const imageUrl = parsed?.data?.[0]?.url || parsed?.data?.[0]?.b64_json;
          if (!imageUrl) return reject(new Error("API 返回中没有图片数据"));

          // 如果返回的是 base64，直接写入文件
          if (imageUrl.startsWith("data:")) {
            const base64 = imageUrl.split(",")[1] || imageUrl;
            fs.writeFileSync(output, Buffer.from(base64, "base64"));
            resolve({ path: path.resolve(output) });
            return;
          }

          // 如果返回的是 URL，下载图片
          const transport = imageUrl.startsWith("https") ? https : http;
          const file = fs.createWriteStream(output);
          transport.get(imageUrl, (imgRes) => {
            if (imgRes.statusCode >= 400) {
              file.close();
              fs.unlink(output, () => {});
              return reject(new Error(`下载图片失败: ${imgRes.statusCode}`));
            }
            imgRes.pipe(file);
            file.on("finish", () => {
              file.close();
              resolve({ path: path.resolve(output) });
            });
          }).on("error", (err) => {
            file.close();
            fs.unlink(output, () => {});
            reject(err);
          });
        } catch (e) {
          reject(new Error(`解析响应失败: ${e.message}`));
        }
      });
    });
    req.on("error", (err) => {
      reject(err);
    });
    req.write(body);
    req.end();
  });
}

async function main() {
  const args = parseArgs();

  // ── 生图模式 ──
  if (args.isGenerate) {
    if (!args.prompt) {
      console.error("用法: node vision.js --generate \"<英文提示词>\" [选项]");
      console.error("  --model <模型>  默认 flux (flux, sd3, sdxl, sd35)");
      console.error("  --width <宽>    默认 1024");
      console.error("  --height <高>   默认 1024");
      console.error("  --output <路径> 输出文件路径");
      process.exit(1);
    }
    if (!SILICONFLOW_API_KEY) {
      console.error("请设置 SILICONFLOW_API_KEY 环境变量或在 .env 文件中配置。");
      console.error("免费获取 Key: https://cloud.siliconflow.cn/account/ak");
      process.exit(1);
    }
    try {
      const result = await generateImage(args.prompt, args);
      console.log(JSON.stringify({ success: true, path: result.path }));
    } catch (err) {
      console.error("生图失败:", err.message);
      process.exit(1);
    }
    return;
  }

  // ── 识图模式 ──
  if (!API_KEY) {
    console.error("请设置 DASHSCOPE_API_KEY 环境变量或在 .env 文件中配置。");
    console.error("获取 Key: https://bailian.console.aliyun.com/");
    process.exit(1);
  }
  if (!args.imageSource) {
    console.error("用法: node vision.js <图片路径> [问题]");
    console.error("      node vision.js --url <图片链接> [问题]");
    console.error("      node vision.js --generate \"<提示词>\" [选项]");
    process.exit(1);
  }
  try {
    const imageUrl = resolveImageUrl(args.imageSource, args.isUrl);
    const result = await request({
      model: MODEL,
      messages: [{ role: "user", content: [
        { type: "image_url", image_url: { url: imageUrl } },
        { type: "text", text: args.prompt },
      ]}],
      stream: false,
      max_tokens: 1024,
    });
    console.log(result);
  } catch (err) {
    console.error("识图失败:", err.message);
    process.exit(1);
  }
}

main();
