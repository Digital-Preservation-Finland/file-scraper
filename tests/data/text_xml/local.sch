<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">

        <sch:ns prefix="local" uri="http://localhost/"/>

	<sch:pattern id="check_body">
		<sch:rule context="local:note">
			<sch:assert test="local:body">
				Element body not found.
			</sch:assert>
		</sch:rule>
	</sch:pattern>
</sch:schema>
