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

# Using .NET libraries becuase Out-File with utf8 encoding always includes
# byte order marks, which the pyhon script can not ingest
$inventory = ConvertTo-Json $inventory
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllLines($Destination, $inventory, $Utf8NoBomEncoding)
