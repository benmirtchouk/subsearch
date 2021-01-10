# subsearch

A tool to automate the usage of subtitle files (derived from the same video but in different languages) in translating words.

While this may seem useless given the quantity of dictionary/translation services available nowadays, it can serve as a great additional resource to aid in language-learning. Most concretely, the use-case this was designed for was for finding "slang-like" expressions and **natural** ways of saying things. 

For example, it is difficult to use a translation tool to answer the question of how one might say "cool!" (to mean passive agreement) or "ew" (to show disgust) or "ouch" (to indicate pain) in a target language. These are all things that can be looked up, but by looking at usages in context one can become more comfortable with which words/phrases can be used in which ways (and perhaps more importantly, the ways in which they _cannot_ be used).

The tool can similarly be used to identify the differences in context when using two words that appear to be synonyms when translated.

An unintended use for this is in searching profanity which may have its own educational merit for some (for example if you would like to know how harsh a given word is).

## Usage

```bash
usage: subsearch.py [-h] [--it t_interval] [--iq q_interval] qlang rlang query

Find subtitles containing a word in a query and corresponding reference language.

positional arguments:
  qlang            the query language
  rlang            the reference language
  query            a word to search for in the query language

optional arguments:
  -h, --help       show this help message and exit
  --it t_interval  the minimum number of seconds to keep surrounding a match
  --iq q_interval  the minimum number of subtitles to keep surrounding a match
```

The basic functionality takes in a query language (the one you type your target word in), a reference language (the language you want to align with the query language), and finally the query itself (for now limited to just one word).

```bash
python subsearch.py EN KOR nice
```

There are a few extra parameters for determining which subtitles to include in the final output. For example, if you would like to keep at least 30 seconds of context (before and after) each match, you can use:


```bash
python subsearch.py EN KOR nice --it 30
```

And if you would like to additionally keep at least 5 subtitle lines worth of context (again, before and after) each match, you would use:

```bash
python subsearch.py EN KOR nice --it 30 --iq 5
```

From some minimal testing, it seems that `--it 10 --iq 2` is a good setting to use so this is used by default.

## Input Data

The data is expected to be found in the ./data directory in SRT format. Currently, only subtitles in SRT format are supported. The names of the SRT files should be `{id}_{lang}.srt` where the `id` identifies the video and `lang` identifies the language of the subtitle file. **The `id` should not contain underscores**.

Some sample data for English (EN), Korean (KOR), and Russian (RU) has been provided based on the most popular subtitle files on [opensubtitles](https://opensubtitles.org/). Note that the correspondence between files of the same media is drawn solely from timestamps (not translation of the underlying text), meaning that you need to guarantee on your own that the two subtitle files are synced. The easiest way to ensure this is to only download sets of subtitles that correspond to the same exact video (opensubtitles provides this information and allows you to conveniently filter). 

## Notes

The formatting of the output is based on what looked good in my terminal. You may have to edit your terminal settings to get coherent output (for example choosing a font that displays well in both languages you have chosen). You may also have to edit the line width / some details of the printing in the source file.