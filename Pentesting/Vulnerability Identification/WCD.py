import requests
import argparse
import time
from rich.console import Console
from rich.progress import track
from rich.table import Table

# Initialize console for rich output
console = Console()

# Common web cache delimiters for testing
CACHE_DELIMITERS = [";", "@", ",", "!", "~", "%", "#", "?"]

# Static extensions that may trick caching mechanisms
STATIC_EXTENSIONS = [".css", ".jpg", ".png", ".txt", ".html", ".ico"]


def test_cache_behavior(url, cookies):
    """Send a request and check caching behavior."""
    try:
        response = requests.get(url, cookies=cookies, allow_redirects=True)
        cache_control = response.headers.get("Cache-Control", "None")
        return response, cache_control
    except requests.RequestException as e:
        console.print(f"[bold red]Error connecting to {url}: {e}[/bold red]")
        return None, None


def detect_sensitive_data(response):
    """Check if the response contains user-sensitive content."""
    sensitive_keywords = ["username", "email", "token", "balance", "profile", "session"]
    if response:
        body = response.text.lower()
        for keyword in sensitive_keywords:
            if keyword in body:
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Web Cache Deception Testing Tool")
    parser.add_argument("--url", required=True, help="Base URL to test (e.g., https://example.com/user/profile)")
    parser.add_argument("--cookie", help="User session cookie in 'name=value' format", required=True)
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    base_url = args.url
    user_cookie = {args.cookie.split("=")[0]: args.cookie.split("=")[1]}

    console.print(f"\n[bold blue]Starting Web Cache Deception Test on:[/bold blue] {base_url}\n")

    # Step 1: Test normal user page (expected to be private)
    console.print("[bold yellow]Testing original user page...[/bold yellow]")
    response, cache_control = test_cache_behavior(base_url, user_cookie)

    if response and detect_sensitive_data(response):
        console.print("[green]✔ Sensitive data detected in normal page (expected behavior).[/green]")
    else:
        console.print("[red]✘ No sensitive data detected (unexpected behavior).[/red]")

    console.print(f"Cache-Control Header: {cache_control}\n")

    # Step 2: Test modified URLs with static extensions
    vulnerable_paths = []

    for ext in track(STATIC_EXTENSIONS, description="Testing static extensions for cache deception..."):
        mod_url = f"{base_url}{ext}"
        response, cache_control = test_cache_behavior(mod_url, user_cookie)

        if response:
            if "public" in cache_control or "max-age" in cache_control:
                console.print(f"[bold yellow]⚠ Warning: {mod_url} has caching enabled![/bold yellow]")

            if detect_sensitive_data(response):
                console.print(f"[bold red]❗ Vulnerable: Sensitive data found at {mod_url}[/bold red]")
                vulnerable_paths.append(mod_url)

    # Step 3: Test modified URLs with common web cache delimiters
    for delimiter in track(CACHE_DELIMITERS, description="Testing cache delimiters..."):
        mod_url = f"{base_url}{delimiter}cache"
        response, cache_control = test_cache_behavior(mod_url, user_cookie)

        if response:
            if "public" in cache_control or "max-age" in cache_control:
                console.print(f"[bold yellow]⚠ Warning: {mod_url} has caching enabled![/bold yellow]")

            if detect_sensitive_data(response):
                console.print(f"[bold red]❗ Vulnerable: Sensitive data found at {mod_url}[/bold red]")
                vulnerable_paths.append(mod_url)

    # Step 4: Test cross-user exposure
    console.print("\n[bold yellow]Testing for cross-user exposure...[/bold yellow]")
    anonymous_cookie = {}  # No authentication

    for vuln_url in vulnerable_paths:
        response, _ = test_cache_behavior(vuln_url, anonymous_cookie)

        if response and detect_sensitive_data(response):
            console.print(f"[bold red]❗ CRITICAL: Cached user data is exposed at {vuln_url}[/bold red]")
        else:
            console.print(f"[green]✔ No exposure found for {vuln_url}[/green]")

    # Step 5: Summary
    table = Table(title="Web Cache Deception Test Summary")
    table.add_column("Tested URL", justify="left", style="cyan", no_wrap=True)
    table.add_column("Vulnerable", justify="center", style="red")

    for url in vulnerable_paths:
        table.add_row(url, "YES")

    console.print("\n[bold blue]Final Report:[/bold blue]")
    console.print(table)

    if not vulnerable_paths:
        console.print("[bold green]✔ No Web Cache Deception vulnerabilities detected![/bold green]")
    else:
        console.print("[bold red]❗ Warning: Some endpoints are vulnerable. Implement proper cache-control headers.[/bold red]")


if __name__ == "__main__":
    main()
