# Dayboard

A simple kanban board that lives in your browser. One board, three starting columns, and no setup.

Double-click **index.html** in this folder. The file contains the whole app; it needs no installation, network connection, account, or server.

## Use the board

- Choose **New task** or **Add task** in a column. A title is all you need.
- Drag cards between columns or within a column. You can also click a card and change its **Column**, including on touch screens.
- Click a card to edit its notes. Priority, due date, and tags are tucked into an optional section.
- Search titles, notes, and tags. Moving a filtered card keeps all hidden tasks intact.
- Use a column's **…** button to rename it, change its position, or delete it. Deleting a column moves its tasks to the first remaining column. **Undo** restores a deletion or import until your next change.
- The top-right **…** menu has **Add column**, appearance, **Export backup**, and **Import backup**.
- Press **N** for a new task, **E** for a new event, **/** to search, or **Escape** to close a dialog. Cards and controls also work with Tab and Enter.

## Your data

Tasks save automatically in this browser's local storage. Export JSON backups regularly: clearing browser data removes saved tasks, and a different browser or file location may have separate storage. Keep the HTML file in the same location; a desktop shortcut can open it there.

The board continues to use the previous Kanban storage key (`raf-board-v1-kanban`) and reads the older single-board key (`raf-board-v1`) when needed. Existing cards and custom columns are retained. A new board starts empty with **To do**, **In progress**, and **Done**.

The previous Scrum mode is removed. Its saved data is left untouched. If present in this browser, **Export old Scrum board** appears in the options menu. That file can be imported as the one active board if you want to work from it instead. Importing replaces the current board; export it first to keep a separate copy.

Import checks the board structure before replacing data. A malformed backup leaves your current board intact. If browser storage cannot save, Dayboard shows **Not saved** and asks you to export your work before closing.

## Calendar and daily principle

The calendar shows Monday through Sunday. Use the arrows to browse weeks and **Today** to return to the current week. Choose **Add event** to enter a title, date, optional time, and notes. Click an event to edit or delete it. Events without a time display as all-day events. There is no calendar account connection or automatic synchronization.

A short confidence principle is selected by date when the page opens. These are original lines inspired by *The Confident Mind* by Nate Zinsser, not verified quotations from the book.

Events save separately in browser storage under `raf-dayboard-events-v1` and are included in JSON exports. Importing a backup containing events replaces the event list; the board's Undo action does not restore the previous event list. Export before importing to retain a complete copy.

## Standalone source

This folder contains only the app and this README. No build step or runtime dependencies are needed. It includes no saved tasks, calendar entries, account credentials, or external service integrations. Your entries are stored in your browser, not written back into the HTML file. Exported backups contain your entries; keep them private.
