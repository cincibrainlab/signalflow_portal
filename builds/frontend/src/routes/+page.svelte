<script lang="ts">
	import { onMount } from "svelte"
	import AnimatedBrainBackground from "$lib/components/AnimatedBrainBackground.svelte"

	const WebsiteName = "SignalFlow"
	const WebsiteDescription = "SignalFlow is a centralized platform for storing and analyzing neuroimaging data."
	const WebsiteBaseUrl = "https://signalflow.app"

  
	let commandText = ""
	const fullCommand = "docker run -v /path/to/data:/data docker.io/sfvault"
	let cursorVisible = true
  
	onMount(() => {
	  let i = 0
	  const interval = setInterval(() => {
		if (i < fullCommand.length) {
		  commandText += fullCommand[i]
		  i++
		} else {
		  clearInterval(interval)
		}
	  }, 100)
  
	  setInterval(() => {
		cursorVisible = !cursorVisible
	  }, 500)
	})
  </script>
  
  <svelte:head>
	<title>{WebsiteName}</title>
	<meta name="description" content={WebsiteDescription} />
	<meta property="og:title" content={WebsiteName} />
	
  </svelte:head>
  
  <div class="hero min-h-[60vh] ">
	<div class="hero-content text-center py-12">
	  <div class="max-w-xl">
		<div
		  class="text-xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent mb-4 md:mb-8"
		>
		  SignalFlow
		</div>
  
		<div class="text-4xl md:text-5xl font-bold px-2" style="line-height: 1.2;">
		  Your Centralized
		  <span class="underline decoration-secondary decoration-4 md:decoration-[6px]">Neuroscience Data Hub</span>
		</div>
		<AnimatedBrainBackground />
		<div class="mt-6 md:mt-10 text-sm md:text-lg">
		  Empower your research with a centralized platform for storing, analyzing,
		  and sharing neuroimaging data.
		</div>
		<div class="mt-6 md:mt-2">
		  	<a href="/upload">
				<button class="btn btn-primary btn-sm px-6 mt-3 mx-2">Start</button>
		  	</a>
		  	<a rel="external" href="https://cincibrainlab.github.io/signalflow_portal/">
				<button class="btn btn-primary btn-sm px-6 mt-3 mx-2">Explore Features</button>
			</a>
		</div>
	  </div>
	</div>
  </div>
