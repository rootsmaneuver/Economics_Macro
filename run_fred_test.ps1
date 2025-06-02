$logFile = "c:\Users\Valentin Ivanov\OneDrive\Master_Valentin\Coding\Economics_Macro\fred_api_test.log"

# Write a timestamp
Get-Date | Out-File -FilePath $logFile

# Try to run the Python script and capture output
try {
    $output = python "c:\Users\Valentin Ivanov\OneDrive\Master_Valentin\Coding\Economics_Macro\fred_api_fix.py" 2>&1
    $output | Out-File -FilePath $logFile -Append
    Write-Output "Test completed. Check $logFile for results."
} catch {
    "Error: $_" | Out-File -FilePath $logFile -Append
    Write-Output "Error running test. Check $logFile for details."
}
