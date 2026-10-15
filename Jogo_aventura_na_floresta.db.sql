BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "tipo_utilizador" (
	"id_tipo"	INTEGER,
	"nome_tipo"	TEXT NOT NULL CHECK("nome_tipo" IN ('Jogador', 'Administrador')) UNIQUE,
	PRIMARY KEY("id_tipo" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "utilizador" (
	"id_utilizador"	INTEGER,
	"id_tipo"	INTEGER NOT NULL,
	"username"	TEXT NOT NULL UNIQUE,
	"password_hash"	TEXT NOT NULL,
	"email"	TEXT NOT NULL,
	"data_registo"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"ativo"	INTEGER NOT NULL DEFAULT 1 CHECK("ativo" IN (0, 1)),
	PRIMARY KEY("id_utilizador" AUTOINCREMENT),
	FOREIGN KEY("id_tipo") REFERENCES "tipo_utilizador"("id_tipo")
);
INSERT INTO "tipo_utilizador" VALUES (1,'Jogador');
INSERT INTO "tipo_utilizador" VALUES (2,'Administrador');
INSERT INTO "utilizador" VALUES (1,1,'trix','721a18913caf3792469702355861c8e3:715d76819a5378cbb7e2cb34f9e72bc72c66097d7b161a893adb6da018f1840a','trix@gmail.com','2026-10-14 19:40:04',1);
INSERT INTO "utilizador" VALUES (2,1,'utilizador','ab1c7afba66f13588947138c8f8ae9db:748007010dd60d78252723138a956efadbc579f5a50f22503506685027143436','utilizador@emial.com','2026-10-14 20:02:14',1);
INSERT INTO "utilizador" VALUES (3,1,'Trix','f1021ec63b31ef437b63e501bca75811:61162ae1bd51655b9a6916b5bc1c9e5bd6a6ca597b3364c1f87b1f0535b50be8','trix@gmail.com','2026-10-14 20:03:45',1);
COMMIT;
