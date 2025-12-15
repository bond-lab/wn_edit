from wn import lmf
from wn_edit.editor import WordnetEditor

editor = WordnetEditor(create_new=True, lexicon_id='test', label='Test')
editor.create_synset(pos='n', definition='A dog', words=['dog'])

path = 'test_output.xml'
editor.export(path)
print(f"Exported to: {path}")

# Check the XML
with open(path) as f:
    print(f.read())

resource = lmf.load(path)
lex = resource['lexicons'][0]
print('All keys:', list(lex.keys()))
print('Synsets:', len(lex.get('synsets', [])))
print('LexicalEntry:', len(lex.get('entries', [])))
