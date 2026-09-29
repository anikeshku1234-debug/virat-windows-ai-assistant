import os
import subprocess
from pathlib import Path
from typing import List, Tuple
import win32gui
import win32con

class WindowsTools:
    @staticmethod
    def launch(target: str) -> Tuple[bool, str]:
        """Launches native applications via Windows registered URI protocols or Explorer."""
        try:
            os.startfile(target)
            return True, f"Launched {target}"
        except FileNotFoundError:
            # Fallback for standard system binaries
            try:
                subprocess.Popen([target], shell=True)
                return True, f"Spawned process: {target}"
            except Exception as e:
                return False, f"Failed to execute {target}: {str(e)}"

    @staticmethod
    def open_known_path(keyword: str) -> Tuple[bool, str]:
        user_home = Path.home()
        dirs = {
            "downloads": user_home / "Downloads",
            "documents": user_home / "Documents",
            "desktop": user_home / "Desktop",
            "music": user_home / "Music",
            "videos": user_home / "Videos"
        }
        dest = dirs.get(keyword.lower().strip())
        if dest and dest.exists():
            os.startfile(str(dest))
            return True, f"Opened {keyword.capitalize()} directory."
        return False, f"Directory '{keyword}' not resolved."

    @staticmethod
    def deep_file_search(name_fragment: str, max_depth: int = 4) -> List[str]:
        root = Path.home()
        matched = []
        name_lower = name_fragment.lower()

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune hidden & node_modules directories for speed
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != 'node_modules']
            
            depth = len(Path(dirpath).relative_to(root).parts)
            if depth > max_depth:
                continue

            for f in filenames:
                if name_lower in f.lower():
                    matched.append(os.path.join(dirpath, f))
                    if len(matched) >= 3:
                        return matched
        return matched

    @staticmethod
    def execute_power_routine(mode: str) -> str:
        if mode == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
            return "PC shutdown initiated. Commencing in 10 seconds."
        elif mode == "restart":
            subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
            return "PC restart initiated. Commencing in 10 seconds."
        return "Invalid power state."