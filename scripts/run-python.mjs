import { existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'

const candidates = process.platform === 'win32'
  ? [resolve('.venv/Scripts/python.exe'), 'python']
  : [resolve('.venv/bin/python'), 'python3', 'python']

let selected = candidates.find((candidate) => {
  if (candidate.includes('/') || candidate.includes('\\')) return existsSync(candidate)
  const result = spawnSync(candidate, ['--version'], { stdio: 'ignore' })
  return result.status === 0
})

if (!selected) {
  console.error('No Python runtime found. Run ./scripts/bootstrap.sh first.')
  process.exit(2)
}

const result = spawnSync(selected, process.argv.slice(2), { stdio: 'inherit' })
if (result.error) {
  console.error(result.error.message)
  process.exit(2)
}
process.exit(result.status ?? 1)
