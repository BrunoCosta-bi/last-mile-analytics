"""Testes simples da versão destinada ao GitHub."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPublicacao(unittest.TestCase):
    def test_estrutura_minima(self):
        for rel in (
            'README.md', 'LICENSE', 'CHANGELOG.md', '.gitignore',
            'powerbi/projetogit.pbip',
            'powerbi/projetogit.Report/definition.pbir',
            'powerbi/projetogit.SemanticModel/definition.pbism',
            'data/lastmile_sintetico.csv', 'src/gerar_dados.py',
            'sql/01_schema_views.sql', 'docs/preview_sintetico.png',
        ):
            with self.subTest(arquivo=rel):
                self.assertTrue((ROOT / rel).is_file())

    def test_gitignore_protege_arquivos_locais(self):
        text = (ROOT / '.gitignore').read_text(encoding='utf-8')
        for pattern in ('**/.pbi/', '**/cache.abf', '**/localSettings.json'):
            self.assertIn(pattern, text)

    def test_leitura_responsavel_das_imagens(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('não é uma captura do Power BI', readme)
        self.assertIn('100% sintéticos', readme)


if __name__ == '__main__':
    unittest.main()
