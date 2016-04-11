"""Test the remove_unneeded_warnings function. Needs to be in a separate file,
because xmllint_test.py uses the test case generator:"""
from ipt.validator.xmllint import remove_unneeded_warnings


TEXT = (
"/home/spock/scratch/information-package-tools/include/share/schema/mets/mets.xsd:16: "
"element import: Schemas parser warning : Element "
"'{http://www.w3.org/2001/XMLSchema}import': Skipping import of schema "
"located at "
"'/home/spock/scratch/information-package-tools/include/share/schema/external/w3/xml.xsd' "
"for the namespace 'http://www.w3.org/XML/1998/namespace', since this "
"namespace was already imported with the schema located at "
"'http://www.w3.org/2001/xml.xsd'.")


def test_remove_unneeded_warnings():
    """Test the remove_unneeded_warnings function"""
    filtered_text = remove_unneeded_warnings(TEXT)
    assert len(filtered_text) == 0
    filtered_text = remove_unneeded_warnings("foo")
    assert len(filtered_text) == 3
