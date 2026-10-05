# Round 43: compound anims (COMPOUND=1). Usage: render_all43.ps1 [job ...]
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$env:COMPOUND = "1"
$jobs = $args
if ($jobs.Count -eq 0) { $jobs = @("orbital_hq","halcyon_hq","solace_hq","meridian_hq") }
foreach ($j in $jobs) {
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- $j "$o\scratch\bl" anim > "$o\scratch\log_$j.log" 2>&1
  Write-Output "$j ok=$(Select-String -Path "$o\scratch\log_$j.log" -Pattern DONE -Quiet)"
}
