<script lang="ts">
    import { onMount } from 'svelte';
    import { Button } from "$lib/components/ui/button";
    import { getAnalyses } from '$lib/services/apiService';
    import { goto } from '$app/navigation';

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
            console.log(analyses);
        } catch (error) {
            console.error('Error fetching analyses (page):', error);
        }
    });

    function viewDetails(id: string) {
        console.log(`View details for analysis ${id}`);
        // Implement view details functionality
    }

    function openDashboard(id: string) {
        goto(`/dashboard?id=${id}`);
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
                    Category
                </TableHead>
                <TableHead>
                    Valid Formats
                </TableHead>
                <TableHead>
                    Valid Paradigms
                </TableHead>
                <TableHead>
                    Valid Files
                </TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {#each analyses as analysis}
                <TableRow>
                    <TableCell>{analysis.name}</TableCell>
                    <TableCell>{analysis.analysis_function}</TableCell>
                    <TableCell>{analysis.category}</TableCell>
                    <TableCell>{analysis.valid_formats.join(', ')}</TableCell>
                    <TableCell>{analysis.valid_paradigms.join(', ')}</TableCell>
                    <TableCell>{analysis.valid_files.join(', ')}</TableCell>
                    <TableCell>
                        <Button on:click={() => openDashboard(analysis.deployment_id)}>Open Dashboard</Button>
                    </TableCell>
                </TableRow>
            {/each}
        </TableBody>
    </Table>
</div>