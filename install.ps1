function New-Shortcut {
	param (
		[string]$TargetPath,
		[string]$ShortcutLocation
	)

	$shell = New-Object -ComObject WScript.Shell
	$shortcut = $shell.CreateShortcut($ShortcutLocation)
	$shortcut.TargetPath = $TargetPath
	$shortcut.Save()
}

function Get-OfflineMaster {
	$localAppData = [System.Environment]::GetFolderPath("LocalApplicationData")
	$startupFolder = [System.Environment]::GetFolderPath("Startup")

	$owner = "agatemosu"
	$name = "OfflineMaster"
	$branch = "main"
	$downloadUrl = "https://codeload.github.com/$owner/$name/zip/refs/heads/$branch"

	$tempFile = New-TemporaryFile
	$programDirectory = Join-Path -Path $localAppData -ChildPath $name
	$programEntrypoint = Join-Path -Path $programDirectory -ChildPath "$name-$branch/run.pyw"
	$shortcutPath = Join-Path -Path $startupFolder -ChildPath "run.pyw.lnk"

	If (-Not (Test-Path -Path $programDirectory)) {
		New-Item -Path $programDirectory -ItemType Directory | Out-Null
	}

	Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile
	$tempFile.MoveTo($tempFile.FullName + ".zip")

	Expand-Archive -Path $tempFile -DestinationPath $programDirectory -Force
	New-Shortcut -TargetPath $programEntrypoint -ShortcutLocation $shortcutPath

	$tempFile.Delete()
	Start-Process $programEntrypoint
}

Get-OfflineMaster
