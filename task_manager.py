import curses
import psutil
import time

def draw_monitor(stdscr):
    # Hide cursor
    try:
        curses.curs_set(0)
    except:
        pass
        
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

    stdscr.nodelay(True)
    prev_net = psutil.net_io_counters()

    def get_color(val):
        if val < 50:
            return curses.color_pair(1)
        elif val < 80:
            return curses.color_pair(2)
        else:
            return curses.color_pair(3)

    def safe_addstr(y, x, text, attr=0):
        h, w = stdscr.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        try:
            # Truncate text to fit width and avoid writing to last character of last line
            max_len = w - x - 1
            if y == h - 1: # Last line is extra sensitive
                max_len = w - x - 2
            
            if max_len > 0:
                stdscr.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    def draw_bar(y, x, width, label, val):
        filled = int(width * val / 100)
        bar = "█" * filled + "░" * (width - filled)
        safe_addstr(y, x, f"{label:<12}", curses.color_pair(4))
        safe_addstr(y, x + 13, f"[{bar}] {val:5.1f}%", get_color(val))

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        cpu = psutil.cpu_percent()
        per_cpu = psutil.cpu_percent(percpu=True)
        ram = psutil.virtual_memory()
        net = psutil.net_io_counters()

        # Calculate network speed
        upload = (net.bytes_sent - prev_net.bytes_sent) / 1024
        download = (net.bytes_recv - prev_net.bytes_recv) / 1024
        prev_net = net

        # Title Box
        safe_addstr(0, 2, " SYSTEM MONITOR ", curses.A_BOLD | curses.color_pair(4))
        try:
            stdscr.hline(1, 0, "═", w)
        except:
            pass

        current_y = 2
        
        # CPU Section
        safe_addstr(current_y, 2, "CPU", curses.A_BOLD)
        current_y += 1
        draw_bar(current_y, 2, min(w-20, 40), "Total", cpu)
        current_y += 2

        # Per-core CPU (only show what fits)
        # We need at least 8 lines for RAM, Network, and Footer
        max_core_y = h - 8
        for i, core in enumerate(per_cpu):
            if current_y >= max_core_y:
                safe_addstr(current_y, 4, "... more cores hidden ...", curses.color_pair(2))
                current_y += 1
                break
            draw_bar(current_y, 4, min(w-25, 30), f"Core {i}", core)
            current_y += 1

        current_y += 1
        
        # RAM Section
        if current_y < h - 4:
            safe_addstr(current_y, 2, "Memory", curses.A_BOLD)
            current_y += 1
            draw_bar(current_y, 2, min(w-20, 40), "RAM", ram.percent)
            current_y += 1
            safe_addstr(current_y, 4, f"{ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB", curses.color_pair(4))
            current_y += 2

        # Network Section
        if current_y < h - 2:
            safe_addstr(current_y, 2, "Network", curses.A_BOLD)
            current_y += 1
            safe_addstr(current_y, 4, f"↑ {upload:.1f} KB/s   ↓ {download:.1f} KB/s", curses.color_pair(1))

        # Footer
        if h > 2:
            try:
                stdscr.hline(h - 2, 0, "═", w)
            except:
                pass
            safe_addstr(h - 1, 2, "Press 'q' to quit", curses.color_pair(4))

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord("q"):
            break

        time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(draw_monitor)