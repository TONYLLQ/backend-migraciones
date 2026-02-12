USE SIM
GO


-- ** e.	Pasajero peruano que se identifica bajo la nacionalidad peruana y se le registra con calidad migratoria:
-- ==============================================================================================================================================================================

-- e.1. Análisis:
SELECT 
   mm.uIdPersona,
   mm.dFechaControl,
   mm.sTipo,
   mm.sIdPaisNacionalidad,
   mm.sIdDocumento,
   mm.sNumeroDoc,
   [sCalidadMigratoria] = cm.sDescripcion
FROM SimMovMigra mm
JOIN SimCalidadMigratoria cm ON mm.nIdCalidad = cm.nIdCalidad
WHERE
   mm.bAnulado = 0
   AND mm.bTemporal = 0
   AND mm.dFechaControl >= '2025-01-01 00:00:00.000'
   AND mm.sIdPaisNacionalidad = 'PER'
   AND mm.nIdCalidad != 21 -- 21 | PERUANO

-- ==============================================================================================================================================================================



-- ** f.	Pasajero que cuenta con doble nacionalidad y se presenta como extranjero pero se le registra con nacionalidad peruana pero con número de pasaporte extranjero.
-- ==============================================================================================================================================================================

-- f.1. Peruanos con doble nacionalidad
DROP TABLE IF EXISTS #tmp_doble_nacionalidad_peruanos
SELECT p4.* INTO #tmp_doble_nacionalidad_peruanos
FROM (

   SELECT 
      p3.*,
      [nContarDupliPorNacionalidad] = COUNT(1) OVER (PARTITION BY p3.[sId(Datos+Nacionalidad)]),
      [nContarNacionalidadPER] = SUM(p3.bNacionalidadPER) OVER (PARTITION BY p3.[sId(Datos+Nacimiento)])
   FROM (

      SELECT
         p2.*,
         -- Aux
         [nContarDupliPorNacimiento] = COUNT(1) OVER (PARTITION BY p2.[sId(Datos+Nacimiento)])
      FROM (

         SELECT
            [sId(Datos+Nacimiento)] = REPLACE(
                                          CONCAT(
                                             SOUNDEX(pe.sNombre),
                                             SOUNDEX(pe.sPaterno),
                                             SOUNDEX(pe.sMaterno),
                                             pe.sSexo,
                                             CAST(pe.dFechaNacimiento AS INT),
                                             pe.sIdPaisNacimiento
                                          ),
                                          ' ',
                                          ''
                                       ),
            [sId(Datos+Nacionalidad)] = REPLACE(
                                             CONCAT(
                                                SOUNDEX(pe.sNombre),
                                                SOUNDEX(pe.sPaterno),
                                                SOUNDEX(pe.sMaterno),
                                                pe.sSexo,
                                                CAST(pe.dFechaNacimiento AS INT),
                                                pe.sIdPaisNacionalidad
                                             ),
                                             ' ',
                                             ''
                                          ),
            [uIdPersona] = pe.uIdPersona,
            pe.sIdPaisNacionalidad,
            pe.sIdPaisNacimiento,
            [bNacionalidadPER] = IIF(pe.sIdPaisNacionalidad = 'PER', 1, 0)
         FROM SIM.dbo.SimPersona pe
         WHERE
            pe.bActivo = 1
            AND pe.sIdPaisNacimiento != 'NNN'
            AND pe.sIdPaisNacionalidad != 'NNN'

      ) p2

   ) p3
   WHERE
      p3.[nContarDupliPorNacimiento] = 2 -- Solo 2 registros

) p4
WHERE
   p4.[nContarDupliPorNacimiento] = 2 -- Solo 2 registros
   AND p4.[nContarNacionalidadPER] = 1 -- Cualquiera como `PER`
   AND p4.[nContarDupliPorNacionalidad] = 1 -- Nacionalidades distintas


CREATE NONCLUSTERED INDEX ix_tmp_doble_nacionalidad_peruanos 
   ON #tmp_doble_nacionalidad_peruanos([sId(Datos+Nacimiento)])

-- f.2. Peruanos con doble nacionalidad y movimientos migratorios
DROP TABLE IF EXISTS #tmp_doble_nacionalidad_peruanos_con_mm
SELECT 
   f2.* 
   INTO #tmp_doble_nacionalidad_peruanos_con_mm
FROM (

   SELECT 
      f.*,
      [#] = SUM(f.bMovMigra) OVER (PARTITION BY f.[sId(Datos+Nacimiento)])
   FROM (

      SELECT
         d.*,
         [bMovMigra] = (
                           CASE
                              WHEN EXISTS (SELECT TOP 1 1 FROM SimMovMigra mm WHERE mm.uIdPersona = d.uIdPersona) THEN 1
                              ELSE 0
                           END
         )
      FROM #tmp_doble_nacionalidad_peruanos d

   ) f

) f2
WHERE f2.[#] = 2

-- f.4. Nacionalidad PER y extranjera en únicos registros
DROP TABLE IF EXISTS #tmp_doble_nacionalidad_peruanos_con_mm_final
SELECT 
   -- COUNT(1) -- 238,752
   d1.uIdPersona,
   d1.[sId(Datos+Nacimiento)],
   d1.[sId(Datos+Nacionalidad)],
   d1.sIdPaisNacionalidad,
   [sIdPaisNacionalidad(Otro)] = d2.sIdPaisNacionalidad
   INTO #tmp_doble_nacionalidad_peruanos_con_mm_final
FROM #tmp_doble_nacionalidad_peruanos_con_mm d1
JOIN #tmp_doble_nacionalidad_peruanos_con_mm d2 ON d1.[sId(Datos+Nacimiento)] = d2.[sId(Datos+Nacimiento)]
                                                AND d1.[uIdPersona] != d2.[uIdPersona]


CREATE NONCLUSTERED INDEX ix_tmp_doble_nacionalidad_peruanos_con_mm_final 
   ON #tmp_doble_nacionalidad_peruanos_con_mm_final(uIdPersona, [sIdPaisNacionalidad(Otro)]);

-- f.4. final: Nacionalidad de control migratorio asociada a un registro de otra nacionalidad.
SELECT
   -- TOP 100
   -- d.*
   COUNT(1)
FROM SimMovMigra mm
JOIN #tmp_doble_nacionalidad_peruanos_con_mm_final d ON mm.uIdPersona = d.uIdPersona
                                                     AND mm.sIdPaisNacionalidad = d.[sIdPaisNacionalidad(Otro)] -- Registro con otra nacionalidad

-- ==============================================================================================================================================================================





-- ** h.	Persona extranjera temporal nacional de Países bajos pero se registra con nacionalidad “holandesa”.                                                                              */
-- ==============================================================================================================================================================================

-- h.1 ...
SELECT 
   mm.uIdPersona,
   mm.dFechaControl,
   mm.sTipo,
   mm.sIdPaisNacionalidad,
   mm.sIdDocumento,
   mm.sNumeroDoc,
   [sCalidadMigratoria] = c.sDescripcion,
   [sTipoCalidad] = c.sTipo
FROM SimMovMigra mm
JOIN SimPersona pe ON mm.uIdPersona = pe.uIdPersona
JOIN SimCalidadMigratoria c ON mm.nIdCalidad = c.nIdCalidad
WHERE
   mm.bAnulado = 0
   AND mm.bTemporal = 0
   AND c.sTipo = 'T' -- Temporales
   AND mm.dFechaControl >= '2025-01-01 00:00:00.000'
   -- AND pe.sIdPaisNacionalidad = 'PBA' -- Registro de persona : PBA | PAISES BAJOS
   AND mm.sIdPaisNacionalidad = 'HOL' -- Nacionalidad control: HOL | HOLANDA


/*
   SimMovMigra:
   
      1. bAnulado
      2. bTemporal
      3. dFechaControl
      4. sIdPaisNacionalidad
      5. nIdCalidad
      6. uIdPersona
      7. dFechaControl
      8. sTipo
      9. sIdDocumento
      10. sNumeroDoc

   SimCalidadMigratoria:

      1. nIdCalidad
      2. sDescripcion
      3. sTipo

   SimPersona:

      1. uIdPersona
      2. sNombre
      3. sPaterno
      4. sMaterno
      5. sSexo
      6. dFechaNacimiento
      7. bActivo
      9. sIdPaisNacimiento
      10. sIdPaisNacionalidad

*/

-- ==============================================================================================================================================================================