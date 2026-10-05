# Round 42: the compound mechanic animations (COMPOUND=1, anim view) for every corp.
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$env:COMPOUND = "1"
$jobs = @(@("orbital_hq",""), @("solace_hq",""), @("halcyon_hq",""), @("rebel_cell_hq","dispatch"), @("meridian_hq",""))
foreach ($j in $jobs) {
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- $j[0] "$o\scratch\bl" anim $j[1] > "$o\scratch\log_$($j[0]).log" 2>&1
  Write-Output "$($j[0]) ok=$(Select-String -Path "$o\scratch\log_$($j[0]).log" -Pattern DONE -Quiet)"
}
