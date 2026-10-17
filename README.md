# Claude Code Agents and Automation: Technology Workbook snapshots

Starting files for the Technology Workbook of the Cybrec course [Claude Code Agents and Automation](https://cybrec.com/learn/courses/claude-code-agents-automation/).

Each folder holds the workbook project as it should look at the end of a task, so you can start the next task even if you didn't finish the previous one.

| Folder | Contents | Use it to start |
|---|---|---|
| `task-1-end/` | The bill-splitter app at the end of Task 1 | Task 2 |

## How to use a snapshot

Do your work in your own GitHub repository. This repository only provides the starting files.

```
gh repo clone Cybrec/course-ccaa
mkdir bill-splitter
cp -r course-ccaa/task-1-end/. bill-splitter/
cd bill-splitter
git init
git add -A
git commit -m "Start from task-1-end"
gh repo create bill-splitter --private --source=. --push
```

You can also ask Claude Code to do these steps for you.
