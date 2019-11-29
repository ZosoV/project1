CREATE TABLE "book" (
  "id" serial NOT NULL,
  "isbn" character varying NOT NULL,
  "title" character varying NOT NULL,
  "author" character varying NOT NULL,
  "year" integer NOT NULL,
  "score" numeric NOT NULL DEFAULT '0'
);

CREATE TABLE "user_library" (
  "id" serial NOT NULL,
  "username" character varying NOT NULL,
  "password" character varying NOT NULL
);

CREATE TABLE "reviewer" (
  "id_book" integer NOT NULL,
  "id_user" integer NOT NULL,
  "comment" character varying NOT NULL,
  "score_user" numeric NOT NULL
);

ALTER TABLE "book"
ADD CONSTRAINT "book_id" PRIMARY KEY ("id");

ALTER TABLE "user_library"
ADD CONSTRAINT "user_library_id" PRIMARY KEY ("id"),
ADD CONSTRAINT "user_library_username" UNIQUE ("username");

ALTER TABLE "reviewer"
ADD CONSTRAINT "reviewer_id_book_id_user" PRIMARY KEY ("id_book", "id_user");

ALTER TABLE "reviewer"
ADD FOREIGN KEY ("id_book") REFERENCES "book" ("id");

ALTER TABLE "reviewer"
ADD FOREIGN KEY ("id_user") REFERENCES "user_library" ("id");