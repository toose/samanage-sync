[CmdletBinding()]
Param(
    [Parameter(Position=1)]
    [string] $Path,
    [Parameter(Position=2)]
    [string] $Destination
)

$inventory = @()
$config = Get-Content $Path | ConvertFrom-Json

foreach($domain in $config.Domains) {
    $inventory += Get-ADComputer -Filter * -SearchBase $domain.SearchBase -Server $domain.Server `
        -Properties $config.Properties | Select-Object name, @{n="owner";e={$_.description}}
}

Out-File -FilePath $Destination -InputObject (ConvertTo-Json $inventory)