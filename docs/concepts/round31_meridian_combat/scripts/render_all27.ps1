# Round 27: Blender jobs (Meridian fortress close + maps, the Halcyon Site options, all HQ map sprites for v5).
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$jobs = @(
  @("meridian_hq","close",""), @("halcyon_site","close","court"), @("halcyon_site","close","sphinx2"), @("halcyon_site","close","obelisk"),
  @("meridian_hq","mapprev","wall"), @("meridian_hq","mapprev","bunker"), @("meridian_hq","mapprev","yard"), @("meridian_hq","mapprev","citadel"),
  @("meridian_hq","map",""), @("solace_hq","map",""), @("halcyon_hq","map",""), @("orbital_hq","map",""), @("rebel_cell_hq","map","")
)
foreach ($j in $jobs) {
  $dst = if ($j[1] -eq "map") { "$o\scratch\map" } elseif ($j[1] -eq "mapprev") { "$o\scratch\opt" } else { "$o\scratch\bl" }
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- $j[0] $dst $j[1] $j[2] > "$o\scratch\log_$($j[0])_$($j[1])_$($j[2]).log" 2>&1
  $ok = Select-String -Path "$o\scratch\log_$($j[0])_$($j[1])_$($j[2]).log" -Pattern "DONE" -Quiet
  Write-Output "$($j[0]) $($j[1]) $($j[2]) ok=$ok"
}
