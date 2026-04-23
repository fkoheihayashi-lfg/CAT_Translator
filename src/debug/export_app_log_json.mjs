import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

import { buildAppLogExportPayload } from '../services/exportAppLog.mjs';

async function main() {
  const [, , inputArg, outputArg] = process.argv;

  if (!inputArg || !outputArg) {
    console.error('Usage: node src/debug/export_app_log_json.mjs <raw_app_log.json> <app_log_export.json>');
    process.exit(1);
  }

  const inputPath = resolve(inputArg);
  const outputPath = resolve(outputArg);
  const rawText = await readFile(inputPath, 'utf-8');
  const parsed = JSON.parse(rawText);
  const rawEntries = Array.isArray(parsed) ? parsed : parsed.entries;

  if (!Array.isArray(rawEntries)) {
    console.error('Input JSON must be an array of app log entries or an object with an "entries" array.');
    process.exit(1);
  }

  const payload = buildAppLogExportPayload(rawEntries);
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf-8');

  console.log(`Exported ${payload.entries.length} app log entr${payload.entries.length === 1 ? 'y' : 'ies'} to ${outputPath}`);
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
