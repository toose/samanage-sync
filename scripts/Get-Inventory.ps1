$inventory = @()
$config = Get-Content .\config.json | ConvertFrom-Json

foreach($domain in $config.Domains) {
    $inventory += Get-ADComputer -Filter * -SearchBase $domain.SearchBase -Server $domain.Server `
        -Properties $config.Properties | Select-Object name, @{n="owner";e={$_.description}}
}

Out-File -FilePath "$PSScriptRoot\inventory.json" -InputObject (ConvertTo-Json $inventory)