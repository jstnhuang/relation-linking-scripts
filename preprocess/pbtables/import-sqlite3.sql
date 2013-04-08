CONNECT 'jdbc:derby:pbtables; create=true';

CREATE TABLE str_to_pb_syn (
  vp VARCHAR(32000), 
  pb VARCHAR(32000),
  prob FLOAT,
  count INTEGER
);
CREATE TABLE str_to_pb_tro (
  vp VARCHAR(32000), 
  pb VARCHAR(32000),
  prob FLOAT,
  count INTEGER
);
CREATE TABLE pb_to_pb_syn (
  pb VARCHAR(32000), 
  pb_syn VARCHAR(32000),
  count INTEGER
);
CREATE TABLE pb_to_pb_tro (
  pb VARCHAR(32000), 
  pb_tro VARCHAR(32000),
  count INTEGER
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'STR_TO_PB_SYN',
  'str-to-pb-syn-derby.tsv',
  '	',
  '"',
  null,
  0
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'STR_TO_PB_TRO',
  'str-to-pb-tro-derby.tsv',
  '	',
  '"',
  null,
  0
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'PB_TO_PB_SYN',
  'pb-to-pb-syn-derby.tsv',
  '	',
  '"',
  null,
  0
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'PB_TO_PB_TRO',
  'pb-to-pb-tro-derby.tsv',
  '	',
  '"',
  null,
  0
);
CREATE INDEX str_to_pb_syn_index ON str_to_pb_syn (vp);
CREATE INDEX str_to_pb_tro_index ON str_to_pb_tro (vp);
CREATE INDEX pb_to_pb_syn_index ON pb_to_pb_syn (pb);
CREATE INDEX pb_to_pb_tro_index ON pb_to_pb_tro (pb);
