import unittest

import sys
import os
import io

from .testutils import TLVSchemaTestCase

class Tests(TLVSchemaTestCase):
    
    _quals = ('extensible',
              'optional',
              'private',
              'invariant',
              'nullable',
              'tag-order',
              'schema-order',
              'any-order',
              'range 0..100',
              'length 0..100',
              'tag 42',
              'id 42')
    
    _qualNames = (qual.split(maxsplit=1)[0] for qual in _quals)

    _allQuals = ', '.join(_quals)

    def _checkQualifierNotAllowedErrors(self, errs, allowedQuals, construct):
        errText = ", ".join((str(err) for err in errs))
        for qual in Tests._qualNames:
            qualAllowed = qual in allowedQuals
            qualAccepted = not (('%s qualifier not allowed' % qual) in errText)
            if qualAccepted and not qualAllowed:
                self.fail('%s qualifier unexpectedly allowed on %s' % (qual, construct))
            elif not qualAccepted and qualAllowed:
                self.fail('%s qualifier unexpectedly *disallowed* on %s' % (qual, construct))
    
    def test_Qualifiers_AllowedQualifiers_STRUCTURE(self):
        schemaText = 'test => STRUCTURE [ %s ] { }' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('extensible', 'private', 'nullable', 'invariant', 'tag-order', 'schema-order', 'any-order'),
            construct='STRUCTURE type')

    def test_Qualifiers_AllowedQualifiers_FIELD_GROUP(self):
        schemaText = 'test => FIELD GROUP [ %s ] { }' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=(),
            construct='FIELD GROUP type')

    def test_Qualifiers_AllowedQualifiers_ARRAY(self):
        schemaText = 'test => ARRAY [ %s ] { }' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='ARRAY type')

    def test_Qualifiers_AllowedQualifiers_ARRAY_OF(self):
        schemaText = 'test => ARRAY [ %s ] OF ANY' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='ARRAY OF type')

    def test_Qualifiers_AllowedQualifiers_LIST(self):
        schemaText = 'test => LIST [ %s ] { }' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='LIST type')

    def test_Qualifiers_AllowedQualifiers_LIST_OF(self):
        schemaText = 'test => LIST [ %s ] OF ANY' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='LIST OF type')

    def test_Qualifiers_AllowedQualifiers_CHOICE_OF(self):
        schemaText = 'test => CHOICE [ %s ] OF { }' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable'),
            construct='CHOICE OF type')

    def test_Qualifiers_AllowedQualifiers_INTEGER(self):
        schemaText = 'test => INTEGER [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'range'),
            construct='INTEGER type')

    def test_Qualifiers_AllowedQualifiers_UNSIGNED_INTEGER(self):
        schemaText = 'test => UNSIGNED INTEGER [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'range'),
            construct='UNSIGNED INTEGER type')

    def test_Qualifiers_AllowedQualifiers_FLOAT(self):
        schemaText = 'test => FLOAT [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'range'),
            construct='FLOAT type')

    def test_Qualifiers_AllowedQualifiers_BOOLEAN(self):
        schemaText = 'test => BOOLEAN [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable'),
            construct='BOOLEAN type')

    def test_Qualifiers_AllowedQualifiers_STRING(self):
        schemaText = 'test => STRING [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='STRING type')

    def test_Qualifiers_AllowedQualifiers_BYTE_STRING(self):
        schemaText = 'test => BYTE STRING [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=('nullable', 'length'),
            construct='BYTE STRING type')

    def test_Qualifiers_AllowedQualifiers_ANY(self):
        schemaText = 'test => ANY [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=(),
            construct='ANY type')

    def test_Qualifiers_AllowedQualifiers_NULL(self):
        schemaText = 'test => NULL [ %s ]' % Tests._allQuals
        errs = Tests.loadValidate(schemaText)
        self._checkQualifierNotAllowedErrors(errs, 
            allowedQuals=(),
            construct='NULL type')

    # TODO: test allowed qualifiers on fields, elements and alternates

    def test_Qualifiers_DuplicateQualifiers(self):
        schemaText = 'test => STRUCTURE [ extensible, extensible ] { }'
        errs = Tests.loadValidate(schemaText)
        self.assertEqual(len(errs), 1, msg='Expected 1 error');
        self.assertIn(str(errs[0]), 'duplicate qualifier');

    def test_Qualifiers_RangeArguments(self):
        schemaText = '''
                     test => ARRAY
                     {
                         INTEGER [ range 0..1 ],
                         INTEGER [ range 0..18446744073709551618 ],
                         INTEGER [ range -100..100 ],
                         INTEGER [ range -100.0..100.00000000 ],
                         INTEGER [ range -18446744073709551618..18446744073709551618 ],
                         INTEGER [ range -18446744073709551618..-18446744073709551616 ],
                         INTEGER [ range 8bit ],
                         INTEGER [ range 16bit ],
                         INTEGER [ range 32bit ],
                         INTEGER [ range 64bit ],
                         UNSIGNED INTEGER [ range 0..1 ],
                         UNSIGNED INTEGER [ range 0..18446744073709551618 ],
                         UNSIGNED INTEGER [ range -100..100 ],
                         UNSIGNED INTEGER [ range -18446744073709551618..18446744073709551618 ],
                         UNSIGNED INTEGER [ range -18446744073709551618..-18446744073709551616 ],
                         UNSIGNED INTEGER [ range 8bit ],
                         UNSIGNED INTEGER [ range 16bit ],
                         UNSIGNED INTEGER [ range 32bit ],
                         UNSIGNED INTEGER [ range 64bit ],
                         FLOAT [ range 0..1 ],
                         FLOAT [ range 0..18446744073709551618 ],
                         FLOAT [ range -100..100 ],
                         FLOAT [ range -100.5..100.5 ],
                         FLOAT [ range -18446744073709551618..18446744073709551618 ],
                         FLOAT [ range -18446744073709551618..-18446744073709551616 ],
                         FLOAT [ range -18446744073709551618.5..18446744073709551618.00007 ],
                         FLOAT [ range 32bit ],
                         FLOAT [ range 64bit ]
                     }
                     '''
        errs = Tests.loadValidate(schemaText)
        self.assertNoErrors(errs)
        
        schemaText = 'test => INTEGER [ range 1..0 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertIn('must be >=', str(errs[0]));
        
        schemaText = 'test => INTEGER [ range 100..-100 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertIn('must be >=', str(errs[0]));

        schemaText = 'test => INTEGER [ range 0..1.5 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertIn('must be integers', str(errs[0]));
        
        schemaText = 'test => FLOAT [ range 8bit ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertIn('only 32bit and 64bit range', str(errs[0]));

        schemaText = 'test => FLOAT [ range 16bit ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertIn('only 32bit and 64bit range', str(errs[0]));

    def test_Qualifiers_LengthArguments(self):
        schemaText = '''
                     test => ARRAY
                     {
                         STRING [ length 42 ],
                         STRING [ length 0..1 ],
                         STRING [ length 100..18446744073709551618 ],
                         STRING [ length 0.. ],
                         BYTE STRING [ length 0 ],
                         BYTE STRING [ length 0..1 ],
                         BYTE STRING [ length 100..18446744073709551618 ],
                         BYTE STRING [ length 100.. ],
                         ARRAY [ length 18446744073709551618 ] OF BOOLEAN,
                         ARRAY [ length 1..1 ] OF BOOLEAN,
                         ARRAY [ length 100..18446744073709551618 ] OF NULL,
                         ARRAY [ length 0..0 ] { ANY * },
                         ARRAY [ length 18446744073709551618.. ] { },
                         LIST [ length 1 ] OF ANY,
                         LIST [ length 100..101 ] OF INTEGER,
                         LIST [ length 100..18446744073709551618 ] OF BYTE STRING,
                         LIST [ length 18446744073709551618..18446744073709551618 ] { },
                         LIST [ length 1.. ] OF STRUCTURE { },
                     }
                     '''
        errs = Tests.loadValidate(schemaText)
        self.assertNoErrors(errs)

        schemaText = 'test => STRING [ length 1..0 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertError(errs, 'must be >= lower bound')

        schemaText = 'test => STRING [ length -1..0 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 1)
        self.assertError(errs, 'must be >= 0')

        schemaText = 'test => STRING [ length 0..-1 ]'
        errs = Tests.loadValidate(schemaText)
        self.assertErrorCount(errs, 2)
        self.assertError(errs, 'must be >= 0')
        self.assertError(errs, 'must be >= lower bound')


if __name__ == '__main__':
    unittest.main()
