CONNECT 'jdbc:derby:vntables; create=true';

CREATE TABLE wn_to_vn (
  wn VARCHAR(32000), 
  vn VARCHAR(32000)
);
CREATE TABLE vn_to_vn (
  vn1 VARCHAR(32000), 
  vn2 VARCHAR(32000)
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'WN_TO_VN',
  'wn_to_vn_derby.tsv',
  '	',
  '"',
  null,
  0
);
CALL SYSCS_UTIL.SYSCS_IMPORT_TABLE(
  null,
  'VN_TO_VN',
  'vn_to_vn_derby.tsv',
  '	',
  '"',
  null,
  0
);
CREATE INDEX wn_to_vn_index ON wn_to_vn (wn);
CREATE INDEX vn_to_vn_index ON vn_to_vn (vn1);
