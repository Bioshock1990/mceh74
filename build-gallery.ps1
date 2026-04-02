param(
  [string]$Root = "c:\Users\Artem\Desktop\A website for Vova"
)

$galleryDir = Join-Path $Root "images\gallery"
$previewDir = Join-Path $Root "images\gallery-previews"
$outFile = Join-Path $Root "data\gallery.json"
$ffmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
$existingItems = @()

if (-not (Test-Path $previewDir)) {
  New-Item -ItemType Directory -Path $previewDir | Out-Null
}

$existingByFolder = @{}
if (Test-Path $outFile) {
  try {
    $existingItems = @(Get-Content $outFile -Raw -Encoding UTF8 | ConvertFrom-Json)
    foreach ($item in $existingItems) {
      if ($item.folder) {
        $existingByFolder[$item.folder] = $item
      }
    }
  } catch {
    Write-Warning "Existing gallery.json could not be read. Continuing with meta.json only."
  }
}

$items = @()
Get-ChildItem -Path $galleryDir -Directory | ForEach-Object {
  $folder = $_.Name
  $folderPath = "images/gallery/$folder"
  $metaPath = Join-Path $_.FullName "meta.json"
  $coverImage = Get-ChildItem -Path $_.FullName -File |
    Where-Object { $_.BaseName -eq '1' -and $_.Extension -match '^\.(jpe?g|png|webp)$' } |
    Sort-Object Name |
    Select-Object -First 1
  $previewName = "$folder.jpg"
  $previewPath = Join-Path $previewDir $previewName

  if ($coverImage -and $ffmpeg) {
    & $ffmpeg -y -loglevel error -i $coverImage.FullName -vf "scale='min(640,iw)':-2" -q:v 7 $previewPath
  }

  $existingItem = $existingByFolder[$folderPath]
  if ($existingItem) {
    $items += [pscustomobject]@{
      id = $existingItem.id
      title = $existingItem.title
      price = $existingItem.price
      description = $existingItem.description
      short = $existingItem.short
      folder = $folderPath
      preview = if (Test-Path $previewPath) { "images/gallery-previews/$previewName" } else { $null }
    }
  } elseif (Test-Path $metaPath) {
    try {
      $meta = Get-Content $metaPath -Raw -Encoding UTF8 | ConvertFrom-Json
      $items += [pscustomobject]@{
        id = $folder
        title = $meta.title
        price = $meta.price
        description = $meta.description
        short = $meta.short
        folder = $folderPath
        preview = if (Test-Path $previewPath) { "images/gallery-previews/$previewName" } else { $null }
      }
    } catch {
      Write-Warning "Bad meta.json in $folder"
    }
  }
}

$json = @($items) | ConvertTo-Json -Depth 4
$json | Set-Content -Path $outFile -Encoding UTF8
Write-Host "Generated $outFile with $($items.Count) items."
