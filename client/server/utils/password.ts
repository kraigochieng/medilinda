import { hashPassword, verifyPassword } from "better-auth/crypto";
import bcrypt from "bcryptjs";

// Users migrated from the old FastAPI auth keep their bcrypt hashes.
// Everyone else uses better-auth's default scrypt.
export const isBcryptHash = (hash: string) => /^\$2[abxy]\$/.test(hash);

export const hashUserPassword = (password: string) => hashPassword(password);

export const verifyUserPassword = ({
	hash,
	password,
}: {
	hash: string;
	password: string;
}) =>
	isBcryptHash(hash)
		? bcrypt.compare(password, hash)
		: verifyPassword({ hash, password });
