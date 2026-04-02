$root = "c:\Users\Artem\Desktop\A website for Vova"
$gallery = Join-Path $root "images\gallery"
$folders = Get-ChildItem -Path $gallery -Directory | Sort-Object Name
$first = $folders[0].FullName
$srcPng = Get-ChildItem -Path $first -Filter *.png -File | Sort-Object Name

foreach ($folder in $folders) {
  Get-ChildItem -Path $folder.FullName -Filter *.jpg -File | Remove-Item -Force -ErrorAction SilentlyContinue

  foreach ($file in $srcPng) {
    Copy-Item -Path $file.FullName -Destination $folder.FullName -Force
  }

  $metaPath = Join-Path $folder.FullName "meta.json"
  if (-not (Test-Path $metaPath)) {
    $title = "Диван " + (Get-Culture).TextInfo.ToTitleCase($folder.Name.Replace('-', ' ').Replace('_',' '))
    @"
{
  "title": "$title",
  "price": "30 000 ₽",
  "description": "Удобный диван с большим спальным местом и современным дизайном.",
  "short": "Удобный диван с большим спальным местом."
}
"@ | Set-Content -Path $metaPath -Encoding UTF8
  }
}

$heroDir = Join-Path $root "images\site"
New-Item -ItemType Directory -Path $heroDir -Force | Out-Null
$heroPath = Join-Path $heroDir "hero.png"
if ($srcPng.Count -gt 0) {
  Copy-Item -Path $srcPng[0].FullName -Destination $heroPath -Force
}
