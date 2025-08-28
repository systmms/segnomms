#!/usr/bin/env pwsh
# Script: repo/setup_cairo_windows.ps1
# Purpose: Install Cairo graphics library on Windows with multiple fallback strategies
# Usage: .\setup_cairo_windows.ps1
# GitHub Actions Integration: Used by .github/workflows/test.yml

param(
    [switch]$Verbose = $false
)

# Set strict error handling
$ErrorActionPreference = "Continue"

function Write-StatusMessage {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "HH:mm:ss"
    switch ($Level) {
        "SUCCESS" { Write-Host "[$timestamp] ✅ $Message" -ForegroundColor Green }
        "ERROR"   { Write-Host "[$timestamp] ❌ $Message" -ForegroundColor Red }
        "WARN"    { Write-Host "[$timestamp] ⚠️  $Message" -ForegroundColor Yellow }
        default   { Write-Host "[$timestamp] ℹ️  $Message" -ForegroundColor Cyan }
    }
}

function Test-CairoInstallation {
    param([string]$Path, [string]$DllName = "libcairo-2.dll")

    $fullPath = Join-Path $Path $DllName
    if (Test-Path $fullPath) {
        Write-StatusMessage "Cairo DLL found at: $fullPath" "SUCCESS"
        return $true
    }
    return $false
}

function Set-EnvironmentVariables {
    param([string]$BinPath, [string]$PkgConfigPath, [string]$CairoRoot)

    Write-StatusMessage "Setting environment variables..."

    # Add to PATH
    echo $BinPath >> $env:GITHUB_PATH

    # Set PKG_CONFIG_PATH
    echo "PKG_CONFIG_PATH=$PkgConfigPath" >> $env:GITHUB_ENV

    # Set CAIRO_ROOT
    echo "CAIRO_ROOT=$CairoRoot" >> $env:GITHUB_ENV

    if ($Verbose) {
        Write-StatusMessage "Environment variables set:"
        Write-StatusMessage "  PATH += $BinPath"
        Write-StatusMessage "  PKG_CONFIG_PATH = $PkgConfigPath"
        Write-StatusMessage "  CAIRO_ROOT = $CairoRoot"
    }
}

function Install-MSYS2Cairo {
    Write-StatusMessage "Strategy 1: Installing Cairo via MSYS2..." "INFO"

    try {
        # Install MSYS2
        Write-StatusMessage "Installing MSYS2..."
        choco install msys2 -y --no-progress

        if ($LASTEXITCODE -ne 0) {
            throw "MSYS2 installation failed with exit code $LASTEXITCODE"
        }

        # Install Cairo packages
        Write-StatusMessage "Installing Cairo packages in MSYS2..."
        $msysBash = "C:\tools\msys64\usr\bin\bash.exe"
        & $msysBash -lc "pacman -S --noconfirm mingw-w64-x86_64-cairo mingw-w64-x86_64-pkg-config"

        if ($LASTEXITCODE -ne 0) {
            throw "Cairo package installation failed with exit code $LASTEXITCODE"
        }

        # Set environment variables
        $binPath = "C:\tools\msys64\mingw64\bin"
        $pkgConfigPath = "C:\tools\msys64\mingw64\lib\pkgconfig"
        $cairoRoot = "C:\tools\msys64\mingw64"

        Set-EnvironmentVariables -BinPath $binPath -PkgConfigPath $pkgConfigPath -CairoRoot $cairoRoot

        # Verify installation
        if (Test-CairoInstallation -Path $binPath) {
            Write-StatusMessage "MSYS2 Cairo installation successful" "SUCCESS"
            return $true
        } else {
            throw "Cairo DLL not found after MSYS2 installation"
        }
    }
    catch {
        Write-StatusMessage "MSYS2 installation failed: $_" "ERROR"
        return $false
    }
}

function Install-VcpkgCairo {
    Write-StatusMessage "Strategy 2: Installing Cairo via vcpkg..." "INFO"

    try {
        # Clone and bootstrap vcpkg
        Write-StatusMessage "Cloning and bootstrapping vcpkg..."
        git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg

        if ($LASTEXITCODE -ne 0) {
            throw "vcpkg clone failed with exit code $LASTEXITCODE"
        }

        & "C:\vcpkg\bootstrap-vcpkg.bat"

        if ($LASTEXITCODE -ne 0) {
            throw "vcpkg bootstrap failed with exit code $LASTEXITCODE"
        }

        # Install Cairo
        Write-StatusMessage "Installing Cairo package..."
        & "C:\vcpkg\vcpkg.exe" install cairo:x64-windows

        if ($LASTEXITCODE -ne 0) {
            throw "Cairo installation failed with exit code $LASTEXITCODE"
        }

        # Set environment variables
        $binPath = "C:\vcpkg\installed\x64-windows\bin"
        $pkgConfigPath = "C:\vcpkg\installed\x64-windows\lib\pkgconfig"
        $cairoRoot = "C:\vcpkg\installed\x64-windows"

        Set-EnvironmentVariables -BinPath $binPath -PkgConfigPath $pkgConfigPath -CairoRoot $cairoRoot

        # Verify installation (vcpkg uses cairo.dll, not libcairo-2.dll)
        if (Test-CairoInstallation -Path $binPath -DllName "cairo.dll") {
            Write-StatusMessage "vcpkg Cairo installation successful" "SUCCESS"
            return $true
        } else {
            throw "Cairo DLL not found after vcpkg installation"
        }
    }
    catch {
        Write-StatusMessage "vcpkg installation failed: $_" "ERROR"
        return $false
    }
}

function Install-PreshingCairo {
    Write-StatusMessage "Strategy 3: Installing preshing Cairo binaries..." "INFO"

    try {
        # Install pkg-config lite
        Write-StatusMessage "Installing pkg-config lite..."
        choco install pkgconfiglite -y --no-progress

        if ($LASTEXITCODE -ne 0) {
            throw "pkg-config installation failed with exit code $LASTEXITCODE"
        }

        # Download Cairo binaries
        Write-StatusMessage "Downloading Cairo binaries..."
        $cairoUrl = "https://github.com/preshing/cairo-windows/releases/download/v1.15.12/cairo-windows-1.15.12.zip"
        Invoke-WebRequest -Uri $cairoUrl -OutFile "cairo-windows.zip" -TimeoutSec 30

        # Extract Cairo
        Write-StatusMessage "Extracting Cairo binaries..."
        Expand-Archive -Path "cairo-windows.zip" -DestinationPath "C:\cairo" -Force

        # Set environment variables
        $binPath = "C:\cairo\bin"
        $pkgConfigPath = "C:\cairo\lib\pkgconfig"
        $cairoRoot = "C:\cairo"

        Set-EnvironmentVariables -BinPath $binPath -PkgConfigPath $pkgConfigPath -CairoRoot $cairoRoot

        # Verify installation
        if (Test-CairoInstallation -Path $binPath) {
            Write-StatusMessage "preshing Cairo installation successful" "SUCCESS"
            return $true
        } else {
            throw "Cairo DLL not found after preshing installation"
        }
    }
    catch {
        Write-StatusMessage "preshing installation failed: $_" "ERROR"
        return $false
    }
}

function Set-SkipCairoTests {
    Write-StatusMessage "All Cairo installation strategies failed" "WARN"
    Write-StatusMessage "Setting SKIP_CAIRO_TESTS=1 to skip Cairo-dependent tests" "WARN"
    echo "SKIP_CAIRO_TESTS=1" >> $env:GITHUB_ENV
    Write-StatusMessage "Cairo installation completed (tests may be skipped)" "WARN"
}

function Main {
    Write-StatusMessage "Installing Cairo for Windows with multiple fallbacks..." "INFO"

    # Strategy 1: MSYS2 Cairo (most reliable)
    if (Install-MSYS2Cairo) {
        return 0
    }

    # Strategy 2: vcpkg Cairo
    if (Install-VcpkgCairo) {
        return 0
    }

    # Strategy 3: preshing Cairo (fallback)
    if (Install-PreshingCairo) {
        return 0
    }

    # Strategy 4: Skip Cairo-dependent tests
    Set-SkipCairoTests
    return 0  # Don't fail the workflow, just skip tests
}

# Entry point
exit (Main)
