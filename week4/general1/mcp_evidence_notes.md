# MCP Evidence Notes

This note summarises three tasks completed using the MCP filesystem connector to my local machine, and why a plain chat model (without local filesystem access) could not have completed them.

## Task 1: List files in a local project folder

I asked Claude to list the files in `week3/general2` on my local machine. Claude used the MCP filesystem tool to enumerate the allowed directories, then list the contents of that exact folder, returning the real file names present on disk (SVG assets, a Markdown file, and a Python script).

**Why plain chat couldn't do this:** A plain chat model has no access to my local filesystem. It cannot see what files exist on my machine, in what folders, or with what names. Without MCP, it would have to guess or ask me to paste the list manually — it has no way to independently verify the contents of `week3/general2`.

## Task 2: Identify file types (SVG assets vs Markdown submission)

Using the same directory listing, Claude categorised the files by extension: four `.svg` assets, one `.md` submission file, and one `.py` script.

**Why plain chat couldn't do this:** Classifying real files by type requires first knowing they exist and what they're named. This is only possible with direct, live access to the folder's actual contents via MCP — a plain chat model has no ground truth about my local project structure to classify in the first place.

## Task 3: Read and summarise the Markdown submission

Claude used the MCP filesystem tool to open and read the full contents of `flyrank_week3_curate_images.md` directly from disk, then summarised the final image set (real captures vs generated visuals) and explained the reasoning for choosing real screenshots over AI-generated images for project proof.

**Why plain chat couldn't do this:** The content of that file exists only on my local machine and had never been shared in the conversation. A plain chat model has no mechanism to fetch, open, or read a specific local file path — it can only work with text I explicitly paste in. MCP gave Claude direct read access to the actual file, so the summary reflects the real, current content rather than anything reconstructed or assumed.

## Overall takeaway

All three tasks depended on live, direct access to my local filesystem — listing real directories, distinguishing real file types, and reading real file contents. Plain chat has no persistent or live connection to my machine, so none of these tasks could have been done accurately without the MCP filesystem connector.
