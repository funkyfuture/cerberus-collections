.. generated with version 1.0.1+2016.09 (2016-09-03 13:21:47.722302)

.. code-block:: xml

  <errors document_id="TARDIS" handler_version="1.0.1+2016.09" schema_id="HistMat" validator="cerberus" version="1.0.1">
    <error code="131" id="19eeb72e7e53961c" rule="keyschema">
      <document_path type="tuple">
        <item type="str">a_dict</item>
      </document_path>
      <schema_path type="tuple">
        <item type="str">a_dict</item>
        <item type="str">keyschema</item>
      </schema_path>
      <constraint type="dict">
        <item>
          <key type="str">type</key>
          <value type="str">integer</value>
        </item>
      </constraint>
      <value type="dict">
        <item>
          <key type="int">0</key>
          <value type="str">abc</value>
        </item>
        <item>
          <key type="str">three</key>
          <value type="str">abC</value>
        </item>
        <item>
          <key type="int">2</key>
          <value type="str">aBc</value>
        </item>
        <item>
          <key type="str">one</key>
          <value type="str">abc</value>
        </item>
      </value>
      <error code="36" id="587d53b01314e30b" rule="type">
        <document_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">one</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">keyschema</item>
          <item type="str">type</item>
        </schema_path>
        <constraint type="str">integer</constraint>
        <value type="str">one</value>
      </error>
      <error code="36" id="657d80202d5c531" rule="type">
        <document_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">three</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">keyschema</item>
          <item type="str">type</item>
        </schema_path>
        <constraint type="str">integer</constraint>
        <value type="str">three</value>
      </error>
    </error>
    <error code="132" id="2a1a92c37a236e5" rule="valueschema">
      <document_path type="tuple">
        <item type="str">a_dict</item>
      </document_path>
      <schema_path type="tuple">
        <item type="str">a_dict</item>
        <item type="str">valueschema</item>
      </schema_path>
      <constraint type="dict">
        <item>
          <key type="str">regex</key>
          <value type="str">[a-z]*</value>
        </item>
      </constraint>
      <value type="dict">
        <item>
          <key type="int">0</key>
          <value type="str">abc</value>
        </item>
        <item>
          <key type="str">three</key>
          <value type="str">abC</value>
        </item>
        <item>
          <key type="int">2</key>
          <value type="str">aBc</value>
        </item>
        <item>
          <key type="str">one</key>
          <value type="str">abc</value>
        </item>
      </value>
      <error code="65" id="411b15fe777cfdba" rule="regex">
        <document_path type="tuple">
          <item type="str">a_dict</item>
          <item type="int">2</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">valueschema</item>
          <item type="str">regex</item>
        </schema_path>
        <constraint type="str">[a-z]*</constraint>
        <value type="str">aBc</value>
      </error>
      <error code="65" id="84fcd9e51e5f70d" rule="regex">
        <document_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">three</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_dict</item>
          <item type="str">valueschema</item>
          <item type="str">regex</item>
        </schema_path>
        <constraint type="str">[a-z]*</constraint>
        <value type="str">abC</value>
      </error>
    </error>
    <error code="130" id="63b3432487564ff1" rule="schema">
      <document_path type="tuple">
        <item type="str">a_list</item>
      </document_path>
      <schema_path type="tuple">
        <item type="str">a_list</item>
        <item type="str">schema</item>
      </schema_path>
      <constraint type="dict">
        <item>
          <key type="str">type</key>
          <value type="str">string</value>
        </item>
        <item>
          <key type="str">oneof</key>
          <value type="list">
            <item type="dict">
              <item>
                <key type="str">regex</key>
                <value type="str">[a-z]*</value>
              </item>
            </item>
            <item type="dict">
              <item>
                <key type="str">regex</key>
                <value type="str">[A-Z]*</value>
              </item>
            </item>
          </value>
        </item>
      </constraint>
      <value type="list">
        <item type="int">0</item>
        <item type="str">abc</item>
        <item type="str">abC</item>
      </value>
      <error code="36" id="1119661ac4d0fb94" rule="type">
        <document_path type="tuple">
          <item type="str">a_list</item>
          <item type="int">0</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_list</item>
          <item type="str">schema</item>
          <item type="str">type</item>
        </schema_path>
        <constraint type="str">string</constraint>
        <value type="int">0</value>
      </error>
      <error code="146" id="2c93c34d7a844c5" rule="oneof" definitions="2" validated="0">
        <document_path type="tuple">
          <item type="str">a_list</item>
          <item type="int">2</item>
        </document_path>
        <schema_path type="tuple">
          <item type="str">a_list</item>
          <item type="str">schema</item>
          <item type="str">oneof</item>
        </schema_path>
        <constraint type="list">
          <item type="dict">
            <item>
              <key type="str">regex</key>
              <value type="str">[a-z]*</value>
            </item>
          </item>
          <item type="dict">
            <item>
              <key type="str">regex</key>
              <value type="str">[A-Z]*</value>
            </item>
          </item>
        </constraint>
        <value type="str">abC</value>
        <error code="65" id="7f608a065e7f16e4" rule="regex" definition="0">
          <document_path type="tuple">
            <item type="str">a_list</item>
            <item type="int">2</item>
          </document_path>
          <schema_path type="tuple">
            <item type="str">a_list</item>
            <item type="str">schema</item>
            <item type="str">oneof</item>
            <item type="int">0</item>
            <item type="str">regex</item>
          </schema_path>
          <constraint type="str">[a-z]*</constraint>
          <value type="str">abC</value>
        </error>
        <error code="65" id="7f608a5be067cfd7" rule="regex" definition="1">
          <document_path type="tuple">
            <item type="str">a_list</item>
            <item type="int">2</item>
          </document_path>
          <schema_path type="tuple">
            <item type="str">a_list</item>
            <item type="str">schema</item>
            <item type="str">oneof</item>
            <item type="int">1</item>
            <item type="str">regex</item>
          </schema_path>
          <constraint type="str">[A-Z]*</constraint>
          <value type="str">abC</value>
        </error>
      </error>
    </error>
    <error code="68" id="02d55fba1d20da1" rule="allowed">
      <document_path type="tuple">
        <item type="str">fibonacci</item>
      </document_path>
      <schema_path type="tuple">
        <item type="str">fibonacci</item>
        <item type="str">allowed</item>
      </schema_path>
      <constraint type="list">
        <item type="int">1</item>
        <item type="int">2</item>
        <item type="int">3</item>
        <item type="int">5</item>
        <item type="int">8</item>
        <item type="int">13</item>
        <item type="int">21</item>
        <item type="int">34</item>
        <item type="int">55</item>
        <item type="int">89</item>
      </constraint>
      <value type="int">42</value>
      <info type="int">42</info>
    </error>
    <error code="6" id="e6b01805d54da29" rule="excludes">
      <document_path type="tuple">
        <item type="str">fibonacci</item>
      </document_path>
      <schema_path type="tuple">
        <item type="str">fibonacci</item>
        <item type="str">excludes</item>
      </schema_path>
      <constraint type="list">
        <item type="str">a_dict</item>
        <item type="str">a_list</item>
      </constraint>
      <value type="int">42</value>
      <info type="str">'a_dict', 'a_list'</info>
    </error>
  </errors>

