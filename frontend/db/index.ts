import { drizzle } from "drizzle-orm/d1";
import * as schema from "./schema";

export function getDb() {
  throw new Error("D1 is not used by this local Phase 1 application.");
}
