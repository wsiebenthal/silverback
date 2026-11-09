import subprocess

from silverback.backends import LinuxBackend, MacOSBackend


def _completed(cmd, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr=stderr)


def test_linux_minimize_issues_xdotool_commands():
    calls = []

    def runner(cmd, **_kwargs):
        calls.append(cmd)
        if cmd[1] == "search":
            return _completed(cmd, stdout="42\n7\n")
        if cmd[1] == "getwindowname":
            name = "Project Notes" if cmd[2] == "42" else "Unrelated"
            return _completed(cmd, stdout=name + "\n")
        return _completed(cmd)

    backend = LinuxBackend(runner=runner, which=lambda _name: "/usr/bin/xdotool")
    result = backend.minimize_matching("Notes")
    assert result.ok
    assert result.detail == "minimized 1 window(s): Project Notes"
    assert calls[0][:4] == ["xdotool", "search", "--onlyvisible", "--name"]
    assert calls[0][4] == "Notes"
    assert ["xdotool", "windowminimize", "42"] in calls
    assert ["xdotool", "windowminimize", "7"] not in calls


def test_linux_escapes_regex_and_reports_a_miss():
    calls = []

    def runner(cmd, **_kwargs):
        calls.append(cmd)
        return _completed(cmd, returncode=1, stdout="")

    backend = LinuxBackend(runner=runner, which=lambda _name: "/usr/bin/xdotool")
    result = backend.minimize_matching("Notes+")
    assert not result.ok
    assert result.implemented
    assert "no visible window" in result.detail
    assert calls[0][4] == "Notes\\+"


def test_linux_empty_match_and_missing_tool_do_not_run_commands():
    def runner(*_args, **_kwargs):
        raise AssertionError("runner should not be called")

    empty = LinuxBackend(runner=runner, which=lambda _name: "/usr/bin/xdotool")
    missing = LinuxBackend(runner=runner, which=lambda _name: None)
    assert "empty match" in empty.minimize_matching("  ").detail
    assert "xdotool" in missing.minimize_matching("Notes").detail


def test_macos_passes_the_title_as_an_argument():
    calls = []

    def runner(cmd, **kwargs):
        calls.append((cmd, kwargs.get("input")))
        return _completed(cmd, stdout="2\n")

    match = 'My "Notes"'
    backend = MacOSBackend(runner=runner, which=lambda _name: "/usr/bin/osascript")
    result = backend.minimize_matching(match)
    assert result.ok
    assert result.detail == "minimized 2 window(s)"
    assert calls[0][0] == ["osascript", "-", match]
    assert match not in calls[0][1]


def test_macos_reports_permission_errors_and_misses():
    def denied(cmd, **_kwargs):
        return _completed(cmd, returncode=1, stderr="Not authorized to send Apple events")

    def miss(cmd, **_kwargs):
        return _completed(cmd, stdout="0\n")

    denied_result = MacOSBackend(runner=denied, which=lambda _name: "/usr/bin/osascript").minimize_matching(
        "Notes"
    )
    miss_result = MacOSBackend(runner=miss, which=lambda _name: "/usr/bin/osascript").minimize_matching(
        "Notes"
    )
    missing_tool = MacOSBackend(runner=denied, which=lambda _name: None).minimize_matching("Notes")
    assert "Not authorized" in denied_result.detail
    assert "no window title" in miss_result.detail
    assert "osascript" in missing_tool.detail
