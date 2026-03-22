import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

const supabaseUrl = 'https://jmvgknkpgkutjigwlvmi.supabase.co'; // ✅ your URL
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptdmdrbmtwZ2t1dGppZ3dsdm1pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExODYyNzYsImV4cCI6MjA2Njc2MjI3Nn0.kMOJaDJGRY_nmM9WbNN6mRzqPXimzDOvOtD7QjPZnmk'; // ✅ your real anon public key

export const supabase = createClient(supabaseUrl, supabaseKey);