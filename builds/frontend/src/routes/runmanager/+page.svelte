<script lang="ts">
    import { onMount } from 'svelte';
    import { Button } from "$lib/components/ui/button";
    import { getAnalyses} from '$lib/services/apiService';

    import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "$lib/components/ui/table"
  import {
    ExternalLink,
    ArrowUpDown,
  } from "lucide-svelte"
  

    let analyses: any[] = [];

    onMount(async () => {
        try {
            analyses = await getAnalyses();
        } catch (error) {
            console.error('Error fetching analyses:', error);
        }
    });

    function viewDetails(id: string) {
        console.log(`View details for analysis ${id}`);
        // Implement view details functionality
    }

    function runAnalysis(id: string) {
        console.log(`Run analysis ${id}`);
        // Implement run analysis functionality
    }
</script>

<div>
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead>
                    Analysis Name
                </TableHead>
                <TableHead>
                    Function
                </TableHead>
                <TableHead>
                    Name
                </TableHead>
                <TableHead>
                    Name
                </TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {#each analyses as analysis}
                <TableRow>
                    <TableCell>{analysis.name}</TableCell>
                    <TableCell>{analysis.analysis_function}</TableCell>
                    <TableCell>{analysis.description}</TableCell>
                    <TableCell>{analysis.category}</TableCell>
                </TableRow>
            {/each}
        </TableBody>
    </Table>
</div>