ruscorpora_tagging
==================

Text tokenization and annotation scripts for Ruscorpora

tokenizer.py: annotates text with sentence <se> and word <w> tags.
Uses punctuation and &lt;p&gt;, &lt;tr&gt;, &lt;td&gt;, &lt;th&gt;, &lt;table&gt;, &lt;body&gt; tags as sentence delimiters.

morpho_tagger.py: adds grammatical analysis &lt;ana&gt; tags to the words.
Will split compound words into extra &lt;w&gt;-parts according to the lemmer output.

<<<<<<< HEAD
annotate_texts.py: the complete two-stage tagging. Used with regular morpho_tagger options.

=======
>>>>>>> d9ca10497147713a2691be7c876d7a2e10e63c31
Compiled lemmer binding 'liblemmer_python_binding.so' is needed by morpho_tagger.py and is not in the repository for now.
